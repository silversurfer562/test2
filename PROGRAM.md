# The program

Twelve weeks. Every week builds a capability and lands it as a shipped upgrade
to a named attune package. There is no separate study track and work track —
the training *is* the upgrade work, and the gate is the merged PR.

**Why twelve and not eighteen.** The generic program in `PLAN.md` assumed you
needed to learn eval design, tool design, and memory architecture. The
corrected baseline (`docs/baseline-week-00.md`) shows the attune family
already holds those to a higher standard than the curriculum teaches. So those
weeks are gone rather than padded, and what's left is: three product claims
that aren't yet checkable, three capabilities the family genuinely lacks, and
two weeks making the practice stick.

**Repos in scope:** `Smart-AI-Memory/attune-ai`, `attune-rag`, `attune-forms`,
`attune-verify`. Read at `5a91b6a`, `f00815d`, `4191c4e`, `58aedcb` on
2026-09-11 — verify the module paths below still hold before you start.

**How to read a week.** *Capability* is the rubric dimension it moves.
*Ships in* names the repo and modules. *Gate* is what has to be true, stated so
someone else could check it. Reading is listed only where it's load-bearing;
several weeks have none, because you already do the thing.

---

| Phase | Wk | Week | Ships in |
|---|---|---|---|
| Make the claims checkable | 1 | Cost joined to quality | `attune-rag` |
| | 2–3 | Deletion, proven end to end | `attune-rag`, `attune-ai` |
| | 4–5 | Temporal staleness | `attune-ai` |
| Build what's missing | 6–7 | Session-level failure analysis | `attune-ai` |
| | 8–9 | Durable execution | `attune-ai`, `memdocs` |
| | 10 | Model adaptation | `attune-ai` |
| Make it stick | 11 | The family quality surface | `attune-verify`, `attune-forms` |
| | 12 | Propagation and review | all, plus `deep-study-ai` |

---

# Phase 1 — Make three claims checkable

You sell checkable claims. Three are currently on credit.

> **`PHASE-1.md` is the narrowed charter for this phase** — the entry
> criterion, the shared definition of done, the sequencing argument, and the
> `/spec` mechanics. Read it before starting Week 1.

## Week 1 — Cost joined to quality

**Capability:** cost & latency engineering, 3 → 4.
**Ships in:** `attune-rag` — `src/attune_rag/benchmark.py`,
`docs/specs/release-quality-baseline/thresholds.json`,
`.github/workflows/benchmark.yml`.

`benchmark.py` returns `precision_at_1`, `recall_at_k`, `mean_latency_ms`,
`max_latency_ms`. No cost field. `attune-ai`'s `cost_tracker.py` handles price
history properly — including refusing to mis-price across a model change — and
is wired into no benchmark. Your product thesis is *selectivity × economics*.
Half of it has no number.

**Build**

1. Extract the price table from `attune-ai/src/attune/cost_tracker.py` into
   something `attune-rag` can consume without a dependency inversion —
   `attune-rag` is already a core dependency of `attune-ai`, so the table
   belongs in `attune-rag` and `attune-ai` re-exports, the same move
   `model_tiers.py` already made.
2. Add to the benchmark result dict: `cost_per_query_usd`,
   **`cost_per_successful_query_usd`** (total spend ÷ queries where top-1 hit),
   and `price_table_dated` — the date as a field, not a comment.
3. Add `max_cost_per_successful_query_usd` to `thresholds.json` and a
   `--max-cost` flag that exits 1, mirroring `--min-precision`.
4. Re-publish the README table with a cost column, so the lightweight vs.
   transformer tier rows read as a cost/quality frontier instead of a
   quality-only one.

**Gate.** The Quality gate workflow fails a PR on a cost regression exactly as
it fails one on a precision regression, and the gate comment shows the cost
delta. The published table has a cost column with a date on the price basis.

**Trap.** Cost per *call* instead of cost per *successful* query. The first
number hides retries and re-retrieval; the second is the one an architecture
decision turns on.

---

## Weeks 2–3 — Deletion, proven end to end

**Capability:** safety & data boundaries, 3 → 4.
**Ships in:** `attune-rag` — `src/attune_rag/corpus/base.py`, `directory.py`,
`_aliases.py`, `embedding.py`. Then `attune-ai` — the curated-node path
through Redis hydration and `attune.memory.recall_digest`.

`grep` for `def add|remove|reindex|invalidate|clear` across `attune-rag`'s
corpus, retrieval and embedding modules returns nothing. `CorpusProtocol` is
read-only by construction: `entries()`, `get(path)`, `name`, `version`. There
is no way to remove a document, so there is no test that removal works.

**Two weeks, not one.** The invalidation surface is wider than it looks, and
the honest version of the test is the slow part.

### Week 2 — `attune-rag`

1. Add `MutableCorpusProtocol(CorpusProtocol)` with `remove(path)` and
   `reindex()`. Extending rather than widening keeps every existing read-only
   corpus valid and makes mutability something a corpus opts into.
2. Enumerate the invalidation surfaces before writing the implementation, in
   the spec, in this order:
   - **Entry token cache** — a sidecar on the entry (`entry._tokens_cache`),
     so it dies with the entry. Free.
   - **Embeddings** — separate lifetime. Not free.
   - **Alias and summary maps** — `_aliases.py`, `aliases_override.json`,
     `summaries_override.json`. A removed doc leaving a live alias is a
     dangling pointer that surfaces as a retrieval error much later.
   - **Any persisted index** the corpus implementation writes.
3. `DuplicateAliasError` already exists for the write side; decide and document
   the removal-side equivalent — what happens to an alias whose target is gone.

### Week 3 — `attune-ai`

Delete a curated node and follow it through: the git-backed store, the Redis
hydration, `FCALL recall_digest`'s warm data, the rendered digest, and any
consolidated or summarized memory that quoted it.

**Gate.** A test in both packages' CI that deletes a record, then queries for
something **only that record could answer**, and asserts the answer is gone —
checking index, cache, embeddings, aliases, digest and exports. Red before the
fix, green after. Publish the test's name in the docs so the claim is
checkable by someone who doesn't trust you.

**Trap.** Deleting from the store and not from the derived artifacts. A memory
removed from the graph but still present in a consolidated summary is not
deleted; it's hidden, and hidden is worse because you'll believe the claim.

---

## Weeks 4–5 — Temporal staleness

**Capability:** memory architecture, 3 → 4.
**Ships in:** `attune-ai` — `scripts/memory_recall_eval.py`,
`src/attune/patterns/confidence.py`.

`--phase persistence` runs capture and evaluate in two separate OS processes
to prove recall survives process death. That is real durability testing and
most projects don't have it. **It is not staleness testing.** The two-layer
protocol's central claim — *stale operational memory is worse than none; stale
durable memory fails softly; merging breaks both regimes* — was ratified in
July 2026 and has no test. `get_stale_patterns(days=90)` covers patterns, not
facts that changed.

### Week 4 — Build the scenarios

Add `--phase temporal` to `memory_recall_eval.py`, reusing the existing
multi-process phase architecture rather than writing a second harness. Four
scenario classes, each capturing across ≥ 2 simulated sessions:

| Class | Scenario |
|---|---|
| **T1 changed** | Fact stated in session 1, changed in session 3, queried in session 5 |
| **T2 expired** | A deadline or status that is now past |
| **T3 contradiction** | Two memories, equal confidence, incompatible |
| **T4 injected** | A stored memory carrying directive-shaped text |

T4 is the one to get right: `attune_rag/prompts.py` defends the *retrieval*
path with `<passage>` sentinels. The memory path is a second door into the
same room.

### Week 5 — Conflict presentation and the gate

Decide and implement what reaches the model on a conflict: most recent only,
both with timestamps, or an explicit flag. Different answers are right for
different domains; no answer is wrong in all of them. Then gate it.

**Gate.** **State the target rate before you run it** — the system prefers the
current fact or surfaces the conflict in ≥ X% of cases. Write X down first,
the way the pre-committed go/no-go matrix already works in your specs. Then
wire the phase into the thresholds file so it gates like precision does.

**Trap.** Measuring retrieval recall on the temporal set and calling it
staleness handling. Recall says the current fact *could* be found. It says
nothing about whether the stale one sitting next to it won the slot.

---

# Phase 2 — Build what's missing

Three capabilities the family genuinely lacks. This is the part that is
actually new.

## Weeks 6–7 — Session-level failure analysis

**Capability:** measurement & evaluation, 4 → 4 (widened) and control flow, 3 → 4.
**Ships in:** `attune-ai` — hooks, `telemetry/`, and a new failure taxonomy doc.

Your benchmarks score **queries**. Nothing reads whole **sessions**. A recall
digest can score 100% on precision@1 and still hand the agent the wrong five
things, and no query-level metric will ever show it. This is the single
highest-value unbuilt thing across seven repositories.

### Week 6 — Tracing

Spans across the real session lifecycle: hook fire, git pull, hydrate into
Redis, `FCALL recall_digest`, digest render, recall during the session, capture
at session end. Inputs, outputs, token counts, latency, errors.

**Done means:** you can reconstruct a session from the trace alone, without
the transcript.

### Week 7 — Hand-labelling

Collect ~100 sessions where the memory layer didn't help, or hurt. **Read all
of them by hand.** There is no shortcut that preserves the value. Let the
categories emerge from the traces rather than starting from a list. Rank by
frequency × cost, where cost includes wasted context, latency, and the agent
going down a wrong path confidently.

**Gate.** A ranked taxonomy with counts. For each of the top five: what it
looks like in a trace so you can find it again, the suspected *architectural*
cause, and which workstream addresses it. If nothing in Weeks 8–12 attacks the
top two, re-plan those weeks — the taxonomy outranks this document.

**Trap.** Classifying everything as a retrieval-quality problem, because that's
the lever you have the best instrument for. Most will be selection problems
(the right thing scored well and still lost a slot) or timing problems (it was
hydrated after the agent needed it).

---

## Weeks 8–9 — Durable execution

**Capability:** reliability & failure handling, 3 → 4.
**Ships in:** `attune-ai` — hydrate path, `ops/pending_writes.py`. Then
`memdocs` — `examples/coach/coach.py`.

`pending_writes.py` gets atomicity right via POSIX `O_APPEND`. Circuit
breakers exist in `deep-study-ai`. Neither protects a *run*: nothing
checkpoints, nothing resumes, and no side-effecting operation carries an
idempotency key. Three of your own open items are this work —
git-pull-before-hydrate, stash→curated promotion, and the named future R-item
*crash-safe continuous handoff*.

### Week 8 — `attune-ai`

1. Idempotency keys on every side-effecting memory operation, so a retried
   promotion doesn't double-write a node.
2. A resumable hydrate: checkpoint the boundary, and make a second run after a
   crash converge rather than restart.
3. Close git-pull-before-hydrate with a defined behavior when the pull fails —
   hydrate stale with a warning, or refuse. Pick one and write down why.
4. Crash-safe continuous handoff, per your own R-item.

### Week 9 — `memdocs/coach.py`

The multi-wizard fan-out has no checkpointing and no resumption. Add both.
This is also the week to finally measure the router: the `0.5` confidence
threshold and the per-wizard weights are hand-set and have never been scored
against anything.

**Gate.** Kill the process mid-run, in CI. It resumes and completes with no
duplicated side effects. Plus: a measured routing accuracy number for
`coach.py`, and a decision on whether `0.5` survives contact with it.

**Trap.** Retries that re-execute non-idempotent writes. It is invisible in
testing because you test the happy path, and it is the most common production
failure in agent systems.

---

## Week 10 — Model adaptation

**Capability:** model selection & adaptation, 3 → 4.
**Ships in:** `attune-ai` — a classifier, and `attune-rag/model_tiers.py` if
it ships.

`model_tiers.py` is a clean canonical tier contract with the duplicate mirrors
deliberately retired, and the tiers are measured head-to-head. Selection is
solid. **Adaptation is untouched** — no fine-tune, no distillation anywhere.

**The candidate that suggests itself:** the curation admission decision. Your
curated nodes carry `review_verdict: keep | sharper`, applied by human review
against the 30-day test. That's a labelled dataset for an admission
classifier, generated as a byproduct of work you already did.

**Build**

1. **Check for label drift first.** The verdicts span a period when the policy
   was still settling in July 2026. Split by date and check whether early and
   late labels agree on held-out cases. If they don't, you're training on two
   different policies.
2. Baseline 1: frontier model, prompted with the 30-day test.
3. Baseline 2: small model, prompted. **Do not skip this one** — it's the
   cheapest option and it wins more often than the fine-tuning literature
   suggests.
4. Candidate: small model, LoRA fine-tuned on the verdicts. Held-out split
   with no overlap.

**Gate.** A four-row table — quality, cost per 1k calls, p95 latency,
operational burden — across the three options, plus an ADR that says ship or
don't ship. **Don't ship is a good outcome and is frequently correct.** The
cost of owning a model is real and is rarely counted honestly right after a
good eval result. Count it.

**Trap.** Fine-tuning before you have an eval for the subtask. You'd produce a
model with no way to know it's better.

---

# Phase 3 — Make it stick

## Week 11 — The family quality surface

**Capability:** measurement, 4 → 4 (institutionalized) and tool design
measurement.
**Ships in:** `attune-verify` — `evidence.py`, `checkers/`. And `attune-forms`
— `mcp_server.py`.

Four packages, four harnesses: `attune-rag-benchmark`,
`scripts/memory_recall_eval.py`, `scripts/phase0/lessons_rag_benchmark.py`,
`tests/test_interaction_benchmark_*`. Each measures its package well. There is
no single dated place where all four packages' current numbers live. For a
company whose entire argument is receipts, the receipts are in four drawers.

**Build**

1. **Point `attune-verify` inward.** Declare each harness a truth source.
   `evidence.py` already does sha256 staleness checking on cited documents —
   extend that so a README number whose backing run is older than a stated
   window fails a release check, the way a broken import already does.
2. A family scorecard: every published number across the four packages, with
   its date, its n, its harness command, and its spread.
3. **Measure the MCP tool surface.** `attune-forms` ships typed tools with
   mirrored schemas — excellent design, unmeasured. Build an eval set of
   agent-initiated tool calls and report a tool-error rate: wrong tool chosen,
   malformed arguments, correct call misread. Then gate it.

**Gate.** A release of any attune package fails if a README claim has no
backing truth source, or if its backing number is stale beyond the window.
Tool-error rate published with n and spread.

**Trap.** Building a fifth harness. H5 *indexes* the four; it does not replace
them. Four harnesses that each work is not a problem.

---

## Week 12 — Propagation and review

**Capability:** communicating architecture, 3–4 → 4.
**Ships in:** `deep-study-ai`, all attune repos' `CONTRIBUTING.md` or
`AGENTS.md`.

The baseline's real finding was that solved problems stay inside the package
that solved them. `attune_rag/prompts.py` has shipped passage fencing and an
injection-defense clause for months while `deep-study-ai/claude_service.py:94`
concatenates fetched FDA and PubMed text into the system message unfenced.
That's not a knowledge gap.

**Build**

1. **Port the fix you already wrote** — `<passage>` sentinel wrapping and the
   injection-defense clause — into `deep-study-ai`.
2. **Run `templates/requirements-checklist.md` on a live attune design**, and
   record which of its questions the family already answers by default. That
   diff is the honest measure of the practice.
3. **Write the propagation rule.** Two sentences in `AGENTS.md`: when a
   package solves a cross-cutting problem — prompt assembly, injection
   defense, price history, deletion, idempotency — the solution goes in a
   shared module or gets named in the family checklist. Not a process. A place
   to look before solving it twice.
4. **Run a design review** on the whole memory architecture with reviewers who
   will actually swing.
5. **Re-score the rubric** into `log/rubric-week-12.md` and write the
   retrospective.

**Gate.** The `deep-study-ai` fix is merged. The checklist has been run once on
a live design and revised from what the quarter taught. The propagation rule is
written down. Three substantive objections from the review are recorded and
answered.

**Trap.** A retrospective that lists what you built. Structure it around the
only three questions worth the page: which belief did a measurement kill, which
decision would you reverse today, and what do you now refuse to ship without.

---

## Tracking

| Wk | Gate | PR | Number before | Number after | Date |
|---|---|---|---|---|---|
| 1 | Cost gate live | | — | | |
| 2 | `remove()` + invalidation | | — | | |
| 3 | Deletion test green | | — | | |
| 4 | `--phase temporal` runs | | — | | |
| 5 | Staleness gated at X% | | — | | |
| 6 | Session reconstructible from trace | | — | | |
| 7 | Taxonomy, top 5 with causes | | — | | |
| 8 | Hydrate resumes after kill | | — | | |
| 9 | Fan-out resumes; router scored | | — | | |
| 10 | Three-way table + ship ADR | | — | | |
| 11 | Release fails on stale claim | | — | | |
| 12 | Fix ported; rule written | | — | | |

## What this program deliberately leaves out

- **Multi-agent orchestration.** Cut. It was the first thing cut from the
  generic plan and nothing in the baseline argues for it.
- **A fifth eval framework.** See Week 11's trap.
- **`memdocs` beyond two items.** The stale cost table gets re-dated in Week 1
  and `coach.py` gets durability and a measured router in Week 9. Nothing else
  — it isn't the product.
- **New features in any attune package.** Twelve weeks that ship no roadmap
  features. The argument for spending them is narrow: three of these weeks fix
  claims the family currently makes and cannot check, and the rest buy
  capabilities it doesn't have. If a week can't be defended on one of those two
  grounds, cut it.

## Related documents

| File | What it's for |
|---|---|
| `docs/baseline-week-00.md` | The evidence and corrected scores this program is built on |
| `docs/capability-rubric.md` | The instrument. Score at weeks 0, 6, 12 |
| `docs/attune-hardening.md` | The evidence behind the three surviving gaps; its sequencing is folded into Phase 1 here |
| `templates/requirements-checklist.md` | The pre-design gate, adopted in Week 12 |
| `PLAN.md`, `weeks/` | The generic 12-week template this was derived from — reusable against a different system |
