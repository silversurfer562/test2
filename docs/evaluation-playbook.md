# Evaluation playbook

This is the load-bearing document of the program. Weeks 2 through 12 all
assume you have a working harness from Week 1, because every one of them ends
in a comparison — and a comparison without an eval suite is a vibe.

## Build the set from traces, not from imagination

The single most common failure: writing 40 test cases by hand from what you
*think* users do. They will be cleaner, shorter, and better-formed than real
input, your system will pass them, and you will have measured nothing.

Pull cases from production traces. Stratify:

| Stratum | Share | Why |
|---|---|---|
| Common successful paths | ~40% | Regression protection — these must never break |
| Known failures | ~30% | The set you are trying to move |
| Long tail / weird | ~20% | Where architecture actually shows |
| Adversarial | ~10% | Injection, contradiction, stale data, hostile input |

Fifty well-chosen cases beat five hundred generated ones. You have to be able
to read every failure by hand, or you won't learn anything from a run.

## Three tiers of grading, in this order

**Tier 1 — deterministic.** Did the tool get called? Did the JSON parse? Is
the cited document ID in the retrieved set? Is the number correct? Cheap,
fast, zero variance. Push as much as possible into this tier. Most teams put
far less here than they could, because writing a checkable success criterion
forces you to say what "good" means.

**Tier 2 — LLM judge.** For everything genuinely subjective. Rules that make
it usable:

- Judge one dimension per call. A judge asked for an overall 1–10 returns noise.
- Give it a rubric with concrete anchors, not adjectives.
- **Calibrate against human labels before you trust it.** Label 50 cases
  yourself, run the judge on the same 50, report the agreement rate. Below
  ~80% agreement the judge is measuring something, but not what you think.
- Re-calibrate when you change the judge prompt or the judge model. It's a
  measuring instrument; you re-zero it after you touch it.

**Tier 3 — human.** Spot-check 10 cases per run. Not for the score — for
catching the failure mode your rubric doesn't have a row for yet.

## Report variance or don't report

Run the suite twice on an unchanged system. The spread between those two runs
is your noise floor. Any improvement smaller than the noise floor is not an
improvement, and reporting it as one is how teams talk themselves into
six-week refactors that did nothing.

State results as `72% ± 4 (n=50, 3 runs)`. Always with n. Always with spread.

## Evaluating agents: outcome and trajectory

Outcome-only evals hide the thing you most need to see. An agent that reaches
the right answer after fourteen tool calls, three of them failed retries, has
an architecture problem that a green pass rate will never surface.

Track both:

| | Metric |
|---|---|
| Outcome | Task success rate, answer quality, cost per *successful* task |
| Trajectory | Steps to completion, tool-error rate, redundant calls, context high-water mark, wall-clock p95 |

Cost per successful task, not cost per call — that's the number that makes
the retry loop's price visible.

## Evaluating memory: the eval must span sessions

A memory system evaluated inside one session is being evaluated as a context
window. The interesting behavior only appears across time, so build
multi-session scenarios: facts stated in session 1 and needed in session 5,
facts that change in session 3, facts that should have been forgotten.

Four things to measure, all separately:

1. **Write precision** — of what you stored, what fraction was worth storing?
   Sample 100, hand-label: correct / redundant / wrong.
2. **Read recall under budget** — with a realistic token budget, is the needed
   memory retrieved? Unbounded recall is not the question you have.
3. **Staleness handling** — when a memory is true-but-outdated, does the
   system prefer the current fact, or at minimum surface the conflict?
4. **Deletion** — delete a memory, then ask a question only that memory could
   answer. If the answer still appears, deletion is cosmetic. This is a
   privacy commitment, not a feature, so test it like one.

## Regression gates

Once the suite is stable, wire it in:

- Every change to prompts, tools, retrieval, or memory policy runs the suite.
- A drop beyond the noise floor blocks the merge.
- Cost and p95 latency are gates too, not just quality. A 2% quality gain for
  3x the cost is a decision someone should make on purpose.

## The concession

Evals are necessary and insufficient — both halves at full weight. They will
not catch the failure category you haven't imagined yet, they drift as your
users change, and a system tuned hard against a fixed suite will overfit it.
That's why Tier 3 exists, why you re-sample from traces every few weeks, and
why Week 3 is spent reading failures by hand rather than dashboards.
