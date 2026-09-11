# Baseline read — week 0

**Method and its limits, first.** This is not recollection. I have no memory of
prior sessions with you. This read comes entirely from `attune-agent-memory`
at commit `f79a562` (repo last pushed 2026-09-09), read on 2026-09-11 — 24
files, one repo. It does not see `memdocs`, `deep-study-ai`, `attune-gui-plugin`,
or any private work in progress, and it can only observe what got committed.
Where the evidence runs out below, I say so rather than filling the gap.

Correct the scores. An inaccurate baseline is worse than none.

## The finding: you are past Phase 1 on the memory track, and unmeasured elsewhere

The generic version of this program spends three weeks teaching instrumentation
and three teaching memory architecture. Your repo shows you already do most of
both — on memory. It shows nothing at all on agent control flow, tool design,
durable execution, or the model layer. That asymmetry is the plan.

## What the evidence shows you already do

**Provenance is not an afterthought.** Every curated node carries `node_id`,
`created_at`, `updated_at`, `confidence`, `tags`, `reviewed_at`,
`review_verdict`, `review_response_id`, and typed `edges_json`. That is a
memory *graph* with review history, not a vector store with a label. Week 9's
provenance requirement is already met, and met better than the week asks.

**You have a curation policy with a stated test.** The 30-day test — *will this
still be true and worth carrying in a month?* — is a write-admission rule.
Most systems have no such rule, which is precisely why they degrade.

**You separated the layers for the right reason.** From
`two_layer_memory_protocol_ratified...`: the layers fail oppositely — *stale
operational memory is worse than none (needs machine verification at load);
stale durable memory fails softly (needs human review over time); merging
breaks both regimes.* That is Week 10's thesis, reached independently and
ratified in July. Handoff items citing curated node IDs is the bridge design
this program would have spent a week arriving at.

**Your eval already has a crowding regression class.** `eval_pointer_index.py`
scores three methods head-to-head — `ft` (the feature), `grep` (the baseline),
`desc` (the naive index) — across query classes A (body-only, the value-add
claim), B (paraphrase, any method should pass), C (crowding regression). Method
baselines and a regression class are Week 4 and Week 1 discipline, running
since July.

**You have latency receipts and a token comparison.** `bench_memory.py`:
median of 50, per recall surface, each against its naive Read-first
alternative, with approximate token cost. FCALL 86µs / FT.SEARCH 181µs
medians, cited in the architecture node itself.

**You write real ADRs.** `communication-clarity/decision.md` has four rejected
alternatives with one-line reasons, the constraints that made the decision
reasonable, and four `Revisit when` conditions. That is Week 12 work, done to
a standard most teams never reach.

## The gaps the evidence shows

**Your evals measure the retrieval layer, not the task.** Everything in the
repo scores *did the right file rank top-3* and *how fast*. Nothing scores
*did the session go better because of it*. Those can diverge — retrieval that
looks excellent at top-3 can still lose to the naive alternative once the
model has to use what it got. You have no number for that today.

**n = 12.** `golden_queries.jsonl` has twelve queries across three classes.
Small enough that a single query flipping moves the headline several points,
and there's no run-to-run spread reported anywhere I can see. The methodology
is sound; the sample can't carry the conclusions you'd want to draw from it.

**No cost-per-successful-task.** `bench_memory.py` measures cost per recall
*surface*, which is the right instinct one level too low. The number that
prices an architecture is tokens per task that actually succeeded — it's the
only one that makes retry loops and re-retrieval visible.

**Write precision is reviewed, not measured.** `review_verdict: keep` and
`sharper` show a human review loop, which is more than most systems have. But
there is no sampled precision rate — of what got stored, what fraction was
correct, redundant, or wrong. Review catches individual bad nodes; it doesn't
tell you whether the write path is getting better.

**Nothing on agents, tools, or durability.** No agent loop, no tool-surface
design, no idempotency or checkpointing artifacts in this repo. Possibly they
live elsewhere. If they don't, that's four of the ten rubric dimensions with
no evidence behind them, in a product whose memory layer exists to serve
agents.

**Nothing on the model layer.** No routing, no fine-tune, no distillation, no
model-selection record. The recall path is Redis and RediSearch — classical
retrieval, and well built. Whether a small trained model belongs anywhere in
it is a question the repo doesn't ask.

**One template applied mechanically.** `dispatch_test/decision.md` ships with
the placeholder intact: *"The source material for this record does not name
any rejected alternatives. Fill this in when the alternatives are known."*
That's honest — it names its own gap, which is better than inventing
alternatives. But a decision record with no rejected alternative isn't a
decision record yet, and a template that can be satisfied while empty will be.

## Rubric, scored from evidence

Against `docs/capability-rubric.md`. Evidence-only — dimensions marked *no
evidence* are unscored, not scored zero.

| Dimension | Score | Evidence |
|---|---|---|
| 1. Measurement & evaluation | **2–3** | Method baselines and regression classes (L3 shape) at n=12, retrieval-level only, no variance reported (L2 substance) |
| 2. Context engineering | **3** | Digest vs. read-all-files token comparison in `bench_memory.py`; budget framing implicit in the recall digest |
| 3. Control flow | *no evidence* | Nothing agentic in this repo |
| 4. Tool & interface design | *no evidence* | — |
| 5. Memory architecture | **3, near 4** | Four-layer separation, opposite-failure-mode rationale, typed edges, decay policy, ratified protocol |
| 6. Reliability & failure handling | **2** | `eval_pointer_index.py` waits out the background `FT.CREATE` scan after being bitten twice — real defensive engineering, narrow scope |
| 7. Cost & latency | **2–3** | Latency medians and token approximations per surface; no per-task cost |
| 8. Model selection & adaptation | *no evidence* | — |
| 9. Safety & data boundaries | *no evidence* | No deletion test, permission model, or injection handling in this repo |
| 10. Communicating architecture | **3–4** | ADRs with rejected alternatives and revisit conditions; one empty template |

## What this does to the twelve weeks

| Week | Generic version | Your version |
|---|---|---|
| 1 | Build an eval harness | **Lift the existing harness to task level.** Keep the A/B/C class design; add end-to-end outcome cases, grow past n=50, report run-to-run spread, add cost per successful task |
| 2 | Discover context is a budget | Mostly done. **Spend it on cache-prefix ordering** for the hydrate path and hold the gate at 30% |
| 3 | Build tracing, hand-label failures | **Do this one in full.** Hand-labelling 100 real failing sessions is the highest-value unbuilt thing in your stack |
| 4–7 | Agent architecture | **Do these in full.** Four dimensions with no evidence, on the systems your memory layer exists to serve |
| 8 | Memory reference architecture | **Already written.** Convert it: stop designing, start attacking it. Run the Week 8 review as a red-team of the two-layer protocol |
| 9 | Build the write path | Built. **Measure it** — sample 100 curated nodes, label correct/redundant/wrong, improve, re-measure |
| 10 | Build the read path | Built. **Adversarial set + the deletion test.** You have the theory ratified and no test that proves the system honors it |
| 11 | Model layer | **Do this in full.** Obvious candidate: the curation admission decision itself — a classifier for the 30-day test, distilled from your own review verdicts |
| 12 | Design review | **Raise the bar.** You already write good ADRs; the gate is surviving three substantive objections from reviewers who will actually swing |

Net: Weeks 8–9 compress to about one, and the hours move to Weeks 3–7 and 11.

## The one thing to fix first

Every measurement in the repo answers *did retrieval work*. None answers *did
the agent do better*. Until one does, every architecture decision downstream
of retrieval — how much to store, what to admit, what wins a slot — is being
made on a proxy metric.

Week 1 is where that gets fixed, and it's why Week 1 stays in the plan even
though you already have an eval harness.
