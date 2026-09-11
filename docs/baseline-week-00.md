# Baseline read — week 0

**Method and its limits, first.** This is not recollection; I have no memory of
prior sessions. It is a read of three repositories on 2026-09-11:

| Repo | Commit | Size | Your role | How it's scored |
|---|---|---|---|---|
| `attune-agent-memory` | `f79a562` | 24 files | Yours | Direct evidence |
| `memdocs` | `4df6947` | 189 `.py` | You wrote most of it | Direct evidence |
| `deep-study-ai` | `8c525bc` | 305 `.py` | You set requirements and design; architecture shared with the programmer; your first major team project | **Requirements & design evidence** |

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

## The finding

Reading one repo, the story was "your measurement is retrieval-level." Reading
three, with your role in each, it's sharper:

**Your requirements specify infrastructure reliability a full level above
output reliability.**

The design you set for `deep-study-ai` produced a circuit breaker with
CLOSED / OPEN / HALF_OPEN states, exponential backoff, automatic
cross-provider failover, health status exposed for monitoring, Prometheus,
alembic migrations, and health checks. The module header states the intent
directly — *"Production-grade reliability for healthcare applications."* That
requirement was set, and the build delivered it. Most people running a
clinical app never set it.

The same requirements produced **no golden set, no accuracy measurement, no
hallucination test, and no AI output eval of any kind** — `find` for
`*eval*`, `*golden*`, `*benchmark*` across the repo returns nothing. The
system generates patient education material, discharge instructions, SBAR
reports, and drug-interaction analysis for nurses.

There are 20+ test files. They test contracts, integrations, caching, health,
auth, and deployment. They are tests, not evals, and the distinction is the
whole program. The reliability requirement was stated in a docstring and
built. The correctness requirement was never stated, so nothing was built.

**That is a requirements gap, not a delivery gap** — which is why it belongs
in a baseline about architecture rather than in a note to the engineering
team.

On a first team project, "we never wrote the correctness requirement" is the
single most common omission there is, and it is not the interesting part. The
interesting part is that **the same gap repeats in code you wrote alone,
before and after**: `memdocs` has real round-trip LLM integration tests and no
eval of what those calls return, and `attune-agent-memory` has the most
rigorous measurement of the three and stops at the retrieval layer. One
project's omission is a lesson. The same omission across three independent
systems is a habit, and habits are what a baseline is for.

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

Sources: **D** = direct (attune, memdocs) · **R** = requirements and design
(deep-study-ai).

| Dimension | Score | Src | Evidence |
|---|---|---|---|
| 1. Measurement & evaluation | **2** | D + R | Method baselines and a crowding-regression class (L3 shape) at n=12, retrieval-only, no variance. No output eval specified or built anywhere |
| 2. Context engineering | **3** | D | Cache token accounting, thinking budget, digest vs. read-all-files comparison |
| 3. Control flow | **3** | D | Coach: confidence routing, thresholds, synthesis, fallback, named patterns — code-decided, deliberately. Never measured |
| 4. Tool & interface design | **1** | D | No tool calling in 500+ files you largely wrote |
| 5. Memory architecture | **3, near 4** | D | Four-layer separation, opposite-failure-mode rationale, typed edges, decay policy, ratified protocol |
| 6. Reliability & failure handling | **3** | R + D | Reliability stated as a requirement and delivered: three-state circuit breaker, backoff, failover, health endpoint. Stops at the request boundary, and your own fan-out has no resumption |
| 7. Cost & latency | **2–3** | D | Per-model cost table, token accounting, latency medians. Undated prices, no cost per successful task |
| 8. Model selection & adaptation | **2** | D + R | Provider abstraction with primary/fallback by config. No measured selection, no adaptation, stale pins |
| 9. Safety & data boundaries | **2–3** | R | Systematic disclaimers, clinician-review framing, FHIR behind a service boundary — consistent across a large surface, and yours. Against: no trust boundary specified for inbound external content, and no deletion test on the memory side |
| 10. Communicating architecture | **3–4** | D | ADRs with rejected alternatives and revisit conditions; one empty template |

**Reading the scores:** dimensions 1, 4, 5, 7, 10 rest on code you wrote —
treat those as firm. Dimensions 6 and 9 rest substantially on requirements you
set, which is the right evidence for an architect but has a known blind spot:
it shows what you specified, not what you'd catch in someone else's design.
Week 12's review is where that gets tested.

## What this does to the twelve weeks

| Week | Generic | Your version |
|---|---|---|
| 1 | Build an eval harness | **Build one for output quality on a system you own outright** — `memdocs` wizards, not the clinical app. Keep attune's A/B/C class design. Then take the method to the DSA team as a requirement |
| 2 | Discover context is a budget | Mostly done. Spend it on cache-prefix ordering in the hydrate path; hold the 30% gate |
| 3 | Trace and hand-label failures | **In full.** 100 real failing sessions, read by hand. Nothing in three repos substitutes for this |
| 4 | Pipeline vs agent | You have the pipeline. **Score the router** — the 0.5 threshold and confidence weights in `coach.py` are yours, hand-set, and never measured |
| 5 | Tool interface design | **In full, and it's the widest gap.** Build a tool surface in `memdocs`, where you own the whole stack |
| 6 | Multi-agent | Cut this first if you fall behind |
| 7 | Durable agents | **Half done.** Reliability specified; idempotency, checkpointing, resumption absent from your own fan-out. Then write the inbound trust-boundary requirement — the one whose absence let finding 3 ship |
| 8 | Memory reference architecture | **Already written.** Red-team the two-layer protocol instead of designing it again |
| 9 | Build the write path | Built. **Measure it**: 100 curated nodes, labelled correct / redundant / wrong, improve, re-measure |
| 10 | Build the read path | Built. **Adversarial set + deletion test.** Theory ratified, never tested |
| 11 | Model layer | **In full.** Start by re-dating the cost table in `providers.py` — an afternoon in your own code, and it corrects every cost decision downstream |
| 12 | Design review | **Raise the bar, and flip the chair.** Three substantive objections survived on your own design, then run a review of someone else's. Reviewing is the half your evidence doesn't cover. Ship the requirements checklist below as the week's second artifact |

Net: Weeks 8–9 compress to about one. Those hours go to Weeks 1, 3, 5, and 7.

## The artifact this baseline argues for

By Week 12, write the thing that would have caught all of this on
`deep-study-ai` — **an AI system requirements checklist you run before design
starts.** Not a doc about the past project; a reusable instrument. On the
evidence here, at minimum it asks:

- What measures whether the *output* is correct, and who owns that number?
- What is the trust boundary for content we pull in, not just data we send out?
- What resumes after a mid-run failure, and what does it cost to restart instead?
- What is the cost per successful task, and when was the price table last dated?
- What does deletion actually delete, and how do we prove it?

Five questions. Every one of them is a gap this read found, and every one is
cheap to ask at requirements time and expensive to retrofit. That's the whole
argument for having the checklist.

## The order to start in

1. **Route finding 3 to whoever owns `claude_service.py`.** An afternoon of
   their time, and it closes a live exposure in a deployed clinical system.
   Yours is the follow-up: write the inbound trust-boundary requirement that
   should have existed, in Week 7.
2. **Re-date the cost table and model pins in `providers.py`.** Your code, an
   afternoon, and every cost comparison you make for the next eleven weeks
   rests on it.
3. **Then Week 1** — output eval on a `memdocs` wizard. That's the quarter's
   real work, and it's why Week 1 stays in the plan even though you already
   have a harness.
