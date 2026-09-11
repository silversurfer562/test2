# The plan

## Why this order

Most self-directed AI architecture study starts with agent patterns, because
that's where the interesting papers are. It's the wrong opening, and it fails
quietly: you adopt a pattern, the system feels better, and six weeks later you
cannot say whether it *is* better, because you never had a baseline.

So the first three weeks build nothing new. They instrument what you already
run. That sounds like a waste of a quarter of the program until you try to
answer, in Week 6, whether your orchestrator-worker rewrite was worth a 4x
token bill — and you can.

Weeks 4–7 then work the control-flow layer, 8–10 the memory layer, 11 the
model layer, and 12 puts the whole thing under review. Memory comes *after*
agents deliberately: memory quality is only observable through a system that
uses it, and by Week 8 you'll have one you can measure.

## Calibrated to your baseline

`docs/baseline-week-00.md` reads your actual systems — weighting each by what
you actually did on it — and reweights this plan. The short version: the
attune product family already holds Weeks 1, 5, 8 and 9 to a higher standard
than this program teaches, so those weeks shrink and the hours move to
**Weeks 3, 7 and 11** — session-level failure analysis, durable execution,
and model adaptation, the three things the family doesn't already do.

After Week 12, `docs/attune-hardening.md` is a six-week plan for the three
gaps that survive: unproven deletion, cost detached from quality, and an
untested staleness claim.

The generic week files below stay as written, so that the plan still works
when you re-run it against a different system. The baseline document is the
overlay.

## The twelve weeks

| Wk | Theme | Gate — what has to be true at the end |
|---|---|---|
| 1 | Baseline & eval harness | A reproducible scorecard: pass rate, p50/p95 latency, cost per successful task |
| 2 | Context as a budget | Token spend by category + cache hit rate, then a 30% context cut with no regression |
| 3 | Failure taxonomy | Top failure modes ranked by frequency × cost, each with a suspected architectural cause |
| 4 | Workflow vs agent | Head-to-head table for one feature built both ways, and the number that decided it |
| 5 | Tool interface design | Tool-error rate on the eval suite, before and after a refactor |
| 6 | Delegation & multi-agent | A cost model for a subagent call, and a written rule for when to delegate |
| 7 | Durable agents | Process killed mid-run resumes with no duplicated side effects — demonstrated |
| 8 | Memory reference architecture | A read/write-path design another engineer could implement from, reviewed |
| 9 | Memory write path | Memory precision measured on a labelled sample, improved, re-measured |
| 10 | Memory read path | Adversarial stale/conflicting-memory eval passing, plus a deletion test |
| 11 | Model layer | Quality/cost/latency table across three model options, and a ship-or-don't record |
| 12 | Design review | A review survived with three substantive objections recorded and answered |

## The three capstones

They run *through* the weeks rather than after them. See `projects/README.md`.

1. **Instrumented agent** (Weeks 1–7) — one of your real agents, with an eval
   harness, full tracing, a failure taxonomy, and durable execution.
2. **Memory service** (Weeks 8–10) — the memory layer as a separable component
   with its own evals, measured across sessions rather than within one.
3. **Small model, narrow job** (Week 11) — one subtask moved off a frontier
   model onto a fine-tuned small one, with the decision record either way.

## What you are actually building

Not a portfolio. A set of habits that outlive any particular stack:

- You do not accept a design claim without a measurement or an admitted gap.
- You write the decision down *before* the outcome is known, so you can be
  wrong on the record and learn from it.
- You cost every architectural choice in tokens, latency, and failure rate.
- You can tell the difference between a prompt problem, a context problem,
  and a control-flow problem from a trace.

## Scoring yourself

Score the rubric in `docs/capability-rubric.md` at week 0, week 6, and week 12.
Three data points, same instrument. Save each as `log/rubric-week-NN.md`.

Expect the week-6 score to be *lower* than week 0 in at least one dimension.
That is not a regression — it's the first honest measurement replacing an
estimate. Note it and move on.
