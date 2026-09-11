# After the program: hardening the attune family

**Scope:** `Smart-AI-Memory/attune-ai`, `attune-rag`, `attune-forms`,
`attune-verify`. Six weeks, same cadence as the program, starting after
Week 12. Read on 2026-09-11 at `5a91b6a`, `f00815d`, `4191c4e`, `58aedcb`.

---

## First, a correction

The week-0 baseline was drawn from `attune-agent-memory`, `memdocs`, and
`deep-study-ai`. Its headline — *nothing anywhere measures output quality* —
**is wrong**, and the attune repos are why.

I scored from the weakest sample of your work: a flat-file memory corpus, a
framework repo, and a first team project. The product family is a different
standard entirely:

| What the baseline said was missing | Where it already exists |
|---|---|
| No output eval anywhere | `attune-rag`: precision@1, recall@3, faithfulness, abstention. `attune-ai`: hit@1/hit@3/false-positive with a cross-process persistence phase |
| No regression gates | `attune-rag`'s bundled-corpus row is a hard CI gate; `--min-precision` exits 1 so CI fails. `attune-ai` has a pre-committed go/no-go matrix and a P@3 ≥ 80% cutover gate |
| No held-out evaluation | `attune-rag` publishes numbers on a corpus it has **never seen or been tuned on**, stratified by difficulty, with a hard-paraphrase subset |
| No judge design | `attune_rag/eval/faithfulness.py` decomposes answers into atomic factual claims before scoring |
| Untrusted content unfenced | `prompts.py` wraps every passage in `<passage>` sentinels and ships an explicit injection-defense clause that names the breakout attempt |
| Undated, drifting price tables | `cost_tracker.py:59` refuses to mis-price history across a model change, by name |
| Claims without receipts | `attune-verify` is an entire package for checking numeric claims against declared truth sources |
| No tool surface | `attune_forms/mcp_server.py`, and a released profile corrected by a **live trial** when the measured escaping contradicted the documented claim |

Measurement should have scored **4**, not 2. Tool and interface design should
have scored **4**, not 1. `docs/baseline-week-00.md` carries the corrected
version.

**The real finding is the inverse of the one I wrote.** Your practice is not
behind; it's uneven. The attune family already does the things `deep-study-ai`
needed, and the fix for `claude_service.py:94` has been sitting in
`attune_rag/prompts.py` the whole time. That is a propagation problem, not a
knowledge problem, and it's the last workstream below.

---

## The four gaps that are real

Found by looking for them specifically, after the correction above. Each is
verifiable from the commits named at the top.

### G1 — Deletion is unproven, and `attune-rag` has no path for it at all

`grep` for `def add|remove|reindex|invalidate|refresh|rebuild|clear` across
`attune-rag`'s corpus, retrieval, and embedding modules returns **nothing**. A
corpus is built and queried. There is no documented way to remove a document
and no test that proves removal reaches the index, the retrieval cache
(`retrieval.py:266` keeps cache entries), and the embeddings.

`attune-ai` has `ops/session_redaction.py` and `telemetry` stream deletion, so
the pieces exist — but I found no end-to-end test that deletes a memory and
then asks the question only that memory could answer.

**Why this one is first:** you sell memory. Deletion is the commitment a
memory product makes that it cannot afford to have cosmetic. Every other gap
here costs money or accuracy; this one costs trust, and it's the only one with
a regulatory shadow.

### G2 — Cost is never joined to quality

`attune_rag/benchmark.py` reports `precision_at_1`, `recall_at_k`,
`mean_latency_ms`, `max_latency_ms`. No cost field. `attune-ai` has a careful
`cost_tracker` that handles price history properly — and it is not wired into
any benchmark.

So the quality/**latency** frontier is navigable and the quality/**cost**
frontier is not. Your own product thesis names both sides: *memory hooks
decide what a session carries; caching decides what carrying costs — one
design axis, selectivity times economics.* Half of that axis currently has no
number on it.

### G3 — Persistence is tested; staleness is not

`memory_recall_eval.py --phase persistence` runs capture and evaluate in two
separate OS processes to prove recall survives process death. That's real
durability testing and most projects don't have it.

It is not the same as staleness. The two-layer protocol's central claim —
*stale operational memory is worse than none; stale durable memory fails
softly; merging breaks both regimes* — was ratified in July 2026 and still has
no test. `patterns/confidence.py` has `get_stale_patterns(days=90)` and usage
decay, which covers patterns, not facts that changed.

Nothing in the corpus evaluates: a fact stated in session 1, changed in
session 3, queried in session 5.

### G4 — Four packages, four harnesses, no family surface

`attune-rag-benchmark`, `scripts/memory_recall_eval.py`,
`scripts/phase0/lessons_rag_benchmark.py`, and
`tests/test_interaction_benchmark_*` each measure their own package well.
There is no single dated place where all four packages' current numbers live.

For a company whose entire argument is receipts, the receipts are in four
drawers. And you already own the machine that fixes it — `attune-verify`
checks numeric claims against declared truth sources, which is exactly the
job.

---

## Six weeks

Same rhythm as the program: build, measure, gate, write. Each week names the
program week that paid for it.

### H1–H2 — Deletion, proven end to end *(pays off Week 10)*

**Build.** A corpus mutation API in `attune-rag`: `remove(doc_id)` that
invalidates the retrieval cache and the embeddings, plus `reindex`. In
`attune-ai`, an end-to-end deletion path from a curated node through the Redis
hydration, the recall digest, and any consolidated summary.

**Gate.** A test in both packages' CI that deletes a record, then queries for
something only that record could answer, and asserts the answer is gone —
checking index, cache, embeddings, digest, and exports. Red before the fix,
green after. Publish the test name in the docs so the claim is checkable by
someone who doesn't trust you.

**Two weeks, not one,** because the invalidation surface is wider than it
looks and the honest version of this test is the slow part.

### H3 — Cost joined to quality *(pays off Weeks 1 and 11)*

**Build.** Wire `attune-ai`'s `cost_tracker` into `attune_rag.benchmark`. Add
`cost_per_query_usd` and, where the benchmark knows which queries succeeded,
**`cost_per_successful_query_usd`** — the number that makes re-retrieval and
retry visible. Date the price table in the output, not in a comment.

**Gate.** The published benchmark table gains a cost column, and the model-tier
comparison (lightweight vs transformer) can be read as a cost/quality frontier
rather than a quality-only one. A `--max-cost` flag that exits 1, mirroring
`--min-precision`, so cost regressions fail CI the same way quality ones do.

### H4 — The temporal staleness suite *(pays off Week 10)*

**Build.** A multi-session scenario set for `attune-ai`, modelled on the
existing `--phase` structure: facts that changed between sessions, facts that
expired, two memories of equal confidence that contradict, and a memory
carrying injected content.

**Gate.** State the target rate before you run it. The system prefers the
current fact or surfaces the conflict in ≥ X% of cases. Then wire it as a
gate, the way `attune-rag` already gates precision.

**The point of this week** is that it finally tests the claim the protocol is
built on. Right now that claim is well-reasoned and unmeasured, which is the
one combination your own product argument doesn't accept.

### H5 — One dated quality surface, built on `attune-verify` *(pays off Week 12)*

**Build.** A family scorecard: every published number from all four packages,
each with its date, its n, its harness command, and its spread. Declare the
harnesses as `attune-verify` truth sources so a number that drifts out of date
fails a release check the way a broken import already does.

**Gate.** A release of any attune package fails if a claim in its README has
no backing truth source, or if its backing number is older than a stated
window. That turns the family's marketing claims into checked artifacts —
which is the thing `attune-verify` was built for, pointed inward.

### H6 — Propagation *(pays off Week 12)*

**Build.** Three things, in order:

1. **Port the fix that already exists.** `attune_rag/prompts.py`'s
   `<passage>` sentinel wrapping and injection-defense clause, applied to
   `deep-study-ai`'s `claude_service.py:94`. It is a solved problem inside
   your own org.
2. **Run `templates/requirements-checklist.md` on the next attune design**,
   and record which questions the family already answers by default. That
   diff is the honest measure of the practice.
3. **Write the propagation rule itself.** Two sentences in
   `CONTRIBUTING.md` or `AGENTS.md`: when a package solves a
   cross-cutting problem — prompt assembly, injection defense, price history,
   deletion — the solution goes in a shared module or gets named in the family
   checklist. Not a process. A place to look before solving it again.

**Gate.** The `deep-study-ai` fix is merged, the checklist has been run once
on a live design, and the propagation rule is written down.

---

## What not to fold in

Named so scope stays honest:

- **No new eval frameworks.** Four harnesses that each work is not a problem
  to solve; H5 indexes them, it doesn't replace them.
- **No multi-agent work.** It was the first thing cut from the program and it
  stays cut.
- **No fine-tuning.** Week 11 answers whether it's worth it. If the answer is
  yes, it's a roadmap item, not a hardening item.
- **`memdocs` gets the stale cost table fixed and nothing else.** It's not
  the product.

## The cost of doing this

Six weeks of product time that ships no features. The argument for spending
it is narrow and worth stating plainly: three of these four gaps are places
where **the attune family makes a claim it cannot currently check** — that
deletion deletes, that carrying costs what you say, that stale memory is
handled. You sell checkable claims. Those three are the ones still on credit.

G4 is different — it's not a broken claim, it's four true claims that are hard
for anyone else to verify at once. That one is worth doing because it's cheap
once H1–H4 have produced the numbers, not because anything is wrong.
