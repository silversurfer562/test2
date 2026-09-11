# Eval spec: [what this measures]

## The question

One sentence. What decision will this eval's output inform? If you can't name
the decision, you're building a dashboard, not an eval.

## Dataset

| | |
|---|---|
| Source | (production traces from ___ / synthetic — say which) |
| n | |
| Common paths | % |
| Known failures | % |
| Long tail | % |
| Adversarial | % |
| Refreshed | (date last re-sampled from traces) |

Held-out split: how it's separated, and what guarantees no overlap.

## Grading

**Tier 1 — deterministic.** List each check.

**Tier 2 — LLM judge.** For each judged dimension: the rubric anchors, the
judge model, and the **human agreement rate with the date it was measured**.
Below ~80%, fix the rubric before trusting the output.

**Tier 3 — human spot check.** How many per run, and who.

## Metrics

| Metric | Current | Target | Noise floor |
|---|---|---|---|
| Pass rate | | | ± |
| Cost per successful task | | | ± |
| p50 / p95 latency | | | ± |
| Tool-error rate | | | ± |
| Steps to completion | | | ± |

**Noise floor** = spread across ≥3 runs on an unchanged system. Improvements
smaller than this are not improvements.

## Gate

What blocks a merge. Quality, cost, and latency — all three, or you will trade
one away without noticing.

## Known blind spots

What this eval cannot see. Write it down; it's the list you revisit when
something breaks in production that the suite called green.
