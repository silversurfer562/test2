# Baseline read — week 0

**Method and its limits, first.** This is not recollection; I have no memory of
prior sessions. It is a read of three repositories on 2026-09-11:

| Repo | Commit | Size | Your role | How it's scored |
|---|---|---|---|---|
| `attune-agent-memory` | `f79a562` | 24 files | Yours | Direct evidence |
| `memdocs` | `4df6947` | 189 `.py` | You wrote most of it | Direct evidence |
| `deep-study-ai` | `8c525bc` | 305 `.py` | You set requirements and design; architecture shared with the programmer; your first major team project | **Requirements & design evidence** |
| `Smart-AI-Memory/attune-ai` | `5a91b6a` | 2385 `.py` | Yours — the product | Direct evidence |
| `Smart-AI-Memory/attune-rag` | `f00815d` | 139 `.py` | Yours — the product | Direct evidence |
| `Smart-AI-Memory/attune-forms` | `4191c4e` | 115 `.py` | Yours — the product | Direct evidence |
| `Smart-AI-Memory/attune-verify` | `58aedcb` | 57 `.py` | Yours — the product | Direct evidence |

**The bottom four rows were added after an earlier version of this document
scored you without them, and they change the answer.** See the correction
immediately below. `docs/attune-hardening.md` carries the full comparison and
the post-program plan.

That last row is load-bearing, and it cuts both ways. I don't attribute any
line of `deep-study-ai`'s implementation to you, and I don't score your coding
from it. But requirements and design are exactly the layer this program is
about — so what the system *was asked to do*, and what it was never asked to
do, is direct evidence about your architectural judgment. Implementation-level
findings are flagged as things to route to the code owner.

**And it was your first major project with a team**, which changes what the
gaps mean without changing whether they're real. A requirement you didn't know
to write on your first team project is not a weakness in your judgment — it's
the thing a first team project exists to teach you. So read the gaps below as
a checklist you now have and didn't then, not as a verdict. Where a gap
*repeats* in solo code you wrote before and after, I say so, because that's
the version that matters.

It cannot see private work in progress, anything uncommitted, or
`attune-gui-plugin` and the rest. Where the evidence runs out, I say so.
**Correct the scores** — an inaccurate baseline is worse than none.

---

## The correction that came first

An earlier version of this document was written from `attune-agent-memory`,
`memdocs`, and `deep-study-ai` alone. Its headline — *nothing anywhere
measures output quality* — **was wrong**, and reading the four attune product
repos is what showed it. I had scored the weakest sample of your work: a
flat-file memory corpus, a framework repo, and a first team project.

What the product family actually ships:

- `attune-rag` publishes precision@1, recall@3, faithfulness and abstention
  rates **on a corpus it has never seen or been tuned on**, stratified by
  difficulty, with a hard-paraphrase subset — and gates the bundled-corpus row
  in CI, where `--min-precision` exits 1 on a regression.
- `attune-ai`'s recall eval reports hit@1 / hit@3 / false-positive rate with a
  cross-process persistence phase that proves recall survives process death,
  against a **pre-committed go/no-go matrix** and a P@3 ≥ 80% cutover gate.
- `attune_rag/eval/faithfulness.py` decomposes answers into atomic factual
  claims before scoring them.
- `attune_rag/prompts.py` wraps every retrieved passage in `<passage>`
  sentinels and ships an explicit injection-defense clause that names the
  breakout attempt by example.
- `cost_tracker.py:59` refuses to mis-price history across a model change, by
  name. `model_tiers.py` is a single canonical tier contract with the
  duplicate mirrors deliberately retired.
- `attune-forms` exposes a typed MCP tool surface, and corrected a released
  profile when a **live trial** showed the escaping it documented was not the
  escaping it had.
- `attune-verify` is an entire package for checking numeric claims against
  declared truth sources.

Measurement should have scored **4**, not 2. Tool and interface design **4**,
not 1. The scores below are corrected.

## The finding

**Your practice is not behind. It is uneven, and the unevenness runs in one
direction.**

Every fix the first draft of this document recommended already exists inside
the attune family. The patch for `deep-study-ai`'s unfenced system-message
concatenation has been sitting in `attune_rag/prompts.py` the whole time. The
dated-price-table discipline that `memdocs` lacks is implemented in
`cost_tracker.py`. The CI quality gate that `deep-study-ai` never specified is
running in `attune-rag`.

So the gap this baseline is actually measuring is **propagation**: solved
problems staying inside the package that solved them. That is a different and
much more tractable problem than the one I first wrote down, and it is why
Week 12's artifact is a checklist rather than a curriculum.

Three genuine holes survive the correction, and all three are in the product:
deletion is unproven family-wide, cost is never joined to quality, and the
two-layer protocol's staleness claim has no test. Those are in
`docs/attune-hardening.md`.

## What the evidence shows you already do well

**Memory architecture, at a level most teams never reach** *(attune — yours)*.
Curated nodes carry `node_id`, `created_at`, `updated_at`, `confidence`,
`reviewed_at`, `review_verdict`, `review_response_id`, and typed `edges_json`
— a graph with review history. The 30-day test is a real write-admission
rule. And the two-layer protocol states the thing Week 10 exists to teach:
*the layers fail oppositely — stale operational memory is worse than none;
stale durable memory fails softly; merging breaks both regimes.* Ratified
July 2026.

**Deliberate control flow — the *pipeline* half of Week 4** *(memdocs — yours)*.
`examples/coach/coach.py` routes tasks to wizards with confidence scores, runs
secondaries above a 0.5 threshold, synthesizes outputs, and falls back when
nothing matches. Eight named collaboration patterns (`production_incident` →
Monitoring, Debugging, Retrospective). Code decides the control flow, not the
model. That is the right default and most people don't choose it deliberately.

**Reliability stated as a requirement and delivered** *(deep-study-ai — your
requirements)*. The circuit breaker above. Paired with `eval_pointer_index.py`
waiting out the background `FT.CREATE` scan because querying mid-scan produced
false misses twice on 2026-07-04 — that one is yours directly. Both are the
mark of someone who fixes the class, not the instance.

**Safety framing carried consistently across a large surface**
*(deep-study-ai — your design)*. *"Educational use only — not medical advice.
No PHI stored."* and *"Draft for clinician review"* appear as structured
banners across literature, drug-interaction, risk-assessment, and
document-authoring services, and FHIR/Epic access sits behind its own service
boundary. Consistency at that scale is a design decision, not an accident.

**Cost and caching awareness at the provider layer** *(memdocs — yours)*.
`LLMResponse` carries `tokens_used`; the Anthropic path tracks
`cache_creation_input_tokens` and `cache_read_input_tokens`, sets a thinking
`budget_tokens`, and ships a per-model cost table.

**Real round-trip tests over mocks** *(memdocs — yours)*.
`tests/test_llm_integration.py` makes actual API calls behind `pytest -m llm`,
matching your own curated note on preferring real round-trips. Consistent
principle, applied.

**ADRs with rejected alternatives and revisit conditions** *(attune — yours)*.
`communication-clarity/decision.md` lists four alternatives with one-line
reasons, the constraints, and four revisit triggers. Week 12 standard, already.

## The gaps

**1. Output quality is unmeasured everywhere, including in code you wrote.**
The strongest eval across all three repos is `golden_queries.jsonl` —
**n = 12**, retrieval-level, no run-to-run spread reported. `memdocs` has
none. `deep-study-ai` has none. This is not a delegation artifact; the pattern
holds in the repos that are entirely yours.

**2. No tool calling anywhere — and `memdocs` is yours.** Across 500+ Python
files I found one incidental `input_schema` reference in a doc-generating
wizard. No `tools=`, no `tool_use`, no `tool_choice`. Your systems call models;
they do not give models tools. That is a legitimate design choice, and for a
clinical app it's arguably the right one — but rubric dimension 4 has no
evidence behind it, and you cannot design a tool surface you've never built.
This is the widest genuine gap in the read.

**3. Untrusted content reaches the system message unfenced** *(deep-study-ai —
implementation, not yours)*. `src/services/claude_service.py:94`:

```python
system_message += f"\n\nContext: {context}"
```

`context` carries externally-fetched content — FDA label text, PubMed
abstracts, MyDisease and ClinicalTrials results — concatenated into the
*privileged* half of the prompt with no delimiter, no tagging, and no
instruction that it is data rather than instruction.

**The honest severity:** because the model has no tools, this can't be used to
take actions. The exposure is content manipulation — a crafted string in a
fetched document steering what the nurse is told. In a clinical context that's
the consequence that matters.

**Two separate items come out of this.** The patch is the code owner's: fence
the content in tagged delimiters, move it to the user turn, state in the
system prompt that tagged content is reference data and never instruction.
One afternoon. The requirement is yours: the design specified *"No PHI
stored"* and clinician-review banners, and never specified a trust boundary
for inbound external content. **You set thorough requirements on the data you
send out and none on the data you pull in** — which is exactly the asymmetry
a first-project requirements pass produces, because outbound risk is visible
to everyone in the room and inbound risk isn't. That's Week 7's subject, and
the fix is a checklist rather than a lesson.

**4. Reliability stops at the request boundary.** Circuit breakers and retries
protect single calls. The multi-wizard fan-out in `coach.py` — yours — has no
checkpointing, no resumption, and no idempotency keys. If it dies partway, it
starts over. Week 7's gate is unmet in code you wrote.

**5. Model selection is policy, not measurement — and the pins are stale.**
Primary `claude-3.5-sonnet`, fallback `gpt-4o`, chosen by config. No routing by
task, no measured comparison. The cost table in
`memdocs/empathy_llm_toolkit/providers.py` — your code — is hardcoded Claude
3-era pricing with no date on it. Both are more than a year old as of this
read. An undated price table is the exact failure mode of claiming a number
without dating it, and it will silently misprice every decision made from it.

**6. Write precision is reviewed, not measured** *(attune — yours)*.
`review_verdict: keep` / `sharper` shows a human review loop, which is more
than most systems have. But there's no sampled precision rate, so you can't
tell whether the write path is improving.

**7. One template applied mechanically** *(attune — yours)*.
`dispatch_test/decision.md` ships with the placeholder intact — *"The source
material for this record does not name any rejected alternatives."* Honest,
and better than inventing them. But a template that can be satisfied while
empty eventually will be.

## Rubric, scored from evidence

Sources: **P** = the attune product family · **D** = other direct (attune
corpus, memdocs) · **R** = requirements and design (deep-study-ai).

| Dimension | Score | Src | Evidence |
|---|---|---|---|
| 1. Measurement & evaluation | **4** | P | Held-out unseen corpora, difficulty stratification, pre-committed go/no-go matrices, CI gates that exit 1, a judge that decomposes claims, a live trial that overturned a shipped claim, and a package that checks numeric claims against truth sources |
| 2. Context engineering | **3** | P + D | Passage budgets (`DEFAULT_MAX_CONTEXT_CHARS`), four prompt variants A/B-tested for faithfulness, cache-control handling, digest vs. read-all-files token comparison |
| 3. Control flow | **3** | D | Coach: confidence routing, thresholds, synthesis, fallback, named patterns — code-decided, deliberately. Never measured |
| 4. Tool & interface design | **4** | P | `attune-forms`: typed MCP tools with JSON schemas mirrored across two packages, refusal at build time and collection time, fence-defusing on rendered labels, host profiles corrected by live trial |
| 5. Memory architecture | **3, near 4** | P + D | Four-layer separation, opposite-failure-mode rationale, typed edges, decay policy, ratified protocol, cross-process persistence proven |
| 6. Reliability & failure handling | **3** | P + R + D | Three-state circuit breaker (specified, not written by you), atomic `O_APPEND` writes, bounded probe budgets. Your own Coach fan-out still has no resumption |
| 7. Cost & latency | **3** | P | `cost_tracker` handles price history correctly and by name; benchmarks report mean and max latency. Cost is not joined to quality anywhere |
| 8. Model selection & adaptation | **3** | P | One canonical tier contract, env-overridable, per-call resolution, duplicate mirrors retired — and the tiers measured head-to-head (25% → 90% on hard paraphrases). No adaptation or fine-tuning |
| 9. Safety & data boundaries | **3** | P + R | Explicit injection-defense clause with sentinel wrapping, abstention measured (92% → 8%), session redaction, consistent clinical disclaimers. Deletion unproven family-wide |
| 10. Communicating architecture | **3–4** | D + P | ADRs with rejected alternatives and revisit conditions, numbered D-items in specs, published methodology; one empty template |

**Reading the scores:** the four dimensions carried by the product family
(1, 4, 8, 9) are firm — they rest on shipped, reproducible artifacts. The
weaker scores are 3 (control flow), 6 (reliability), and 7 (cost), and each
has a specific, small piece of unfinished work behind it rather than a missing
capability.

## What this does to the twelve weeks

| Week | Generic | Your version |
|---|---|---|
| 1 | Build an eval harness | **You have four.** Instead: join cost to quality — wire `cost_tracker` into `attune_rag.benchmark` and report cost per *successful* query. The one axis your own thesis names that has no number on it |
| 2 | Discover context is a budget | Largely done. Spend it on cache-prefix ordering in the hydrate path; hold the 30% gate |
| 3 | Trace and hand-label failures | **In full.** 100 real failing sessions, read by hand. Your benchmarks score queries; nothing reads whole sessions. This is still the highest-value unbuilt thing |
| 4 | Pipeline vs agent | You have the pipeline. **Score the router** — `coach.py`'s 0.5 threshold and confidence weights are hand-set and never measured, and `memdocs` is the one place your measuring discipline didn't reach |
| 5 | Tool interface design | **You ship a typed MCP surface.** Instead: measure its tool-error rate against an eval set the way `attune-rag` measures precision. Design is at 4; the measurement of the design isn't |
| 6 | Multi-agent | Cut this first if you fall behind |
| 7 | Durable agents | **The real gap.** Circuit breakers and atomic writes exist; idempotency keys, checkpointing and resumption do not. Kill a `coach.py` fan-out mid-run and make it come back |
| 8 | Memory reference architecture | **Already written and ratified.** Red-team the two-layer protocol instead of designing it again |
| 9 | Build the write path | Built. **Measure it**: 100 curated nodes, labelled correct / redundant / wrong, improve, re-measure |
| 10 | Build the read path | Built and persistence-tested. **Staleness and deletion are not.** The protocol's central claim has no test, and `attune-rag` has no removal path at all |
| 11 | Model layer | Tiers are measured; adaptation is untouched. **Fine-tuning is the only genuinely new thing here** — the curation admission classifier from your `review_verdict` labels |
| 12 | Design review | Raise the bar, and flip the chair. Three substantive objections survived on your own design, then review someone else's. Ship the requirements checklist as the week's second artifact |

Net: Weeks 1, 5, 8 and 9 shrink hard. Those hours go to **Weeks 3, 7 and 11**,
which are now the only weeks teaching something the attune family doesn't
already do.

## The artifact this baseline argues for

The thing that would have caught all of this on `deep-study-ai` is **a
requirements checklist you run before design starts** — not a doc about the
past project, a reusable instrument. It's written:
`templates/requirements-checklist.md`. On the evidence here, it asks:

- What measures whether the *output* is correct, and who owns that number?
- What is the trust boundary for content we pull in, not just data we send out?
- What resumes after a mid-run failure, and what does it cost to restart instead?
- What is the cost per successful task, and when was the price table last dated?
- What does deletion actually delete, and how do we prove it?

Five questions, plus conditional sections for tools, memory, model-decided
control flow, and tenancy. Every one is a gap this read found, and every one
is cheap to ask at requirements time and expensive to retrofit. Run it on your
next design; revise it in Week 12 from what the quarter taught you.

## The order to start in

1. **Port `attune_rag/prompts.py`'s passage fencing to
   `deep-study-ai/claude_service.py:94`.** You already wrote the fix. An
   afternoon, and it closes a live exposure in a deployed clinical system.
2. **Re-date the cost table and model pins in `memdocs/.../providers.py`** —
   the one place your price-history discipline didn't reach. `cost_tracker.py`
   shows what right looks like.
3. **Then Week 1** — join cost to quality in `attune_rag.benchmark`. Small,
   and it completes the axis your product thesis is built on.

After Week 12, `docs/attune-hardening.md` is the six-week plan for the three
gaps that survive this correction: unproven deletion, cost detached from
quality, and an untested staleness claim.
