# Week 1 — Baseline & eval harness

**The question:** What is your system's quality, cost, and latency right now,
stated as numbers you would defend in a review?

## Build

An eval harness over one real system you own. Not a framework — a script you
can read in one sitting.

1. Pull 50–80 cases from production traces, stratified per
   `docs/evaluation-playbook.md` (40% common / 30% known failures / 20% long
   tail / 10% adversarial).
2. Write Tier 1 deterministic checks for everything that can carry one. Push
   harder here than feels natural.
3. Add a Tier 2 LLM judge for what's left. One dimension per judge call, with
   a rubric that has concrete anchors.
4. **Calibrate the judge.** Hand-label 50 cases yourself. Run the judge on the
   same 50. Report the agreement rate in your log. If it's under ~80%, fix the
   rubric before you trust a single number the judge produces.
5. Instrument cost and latency per case. Compute **cost per successful task**,
   not cost per call.

## Study (3h)

Zheng et al. on LLM-as-judge; Anthropic's "Building effective agents"; and two
hours reading your own production traces end to end. See
`docs/reading-list.md`.

## Gate

A scorecard you can hand to someone else, containing:

- Pass rate with n and run-to-run spread — `72% ± 4 (n=60, 3 runs)`
- p50 and p95 latency
- Cost per successful task
- Judge/human agreement rate

Run the whole suite three times on an unchanged system and record the spread.
**That spread is your noise floor for the next eleven weeks.** Every
improvement you claim after this gets compared against it.

## Write

`log/week-01.md`: the scorecard, plus — before you looked at the results —
what you predicted the pass rate would be. Note the gap.

## The trap

Building the eval set from imagined cases instead of traces. Hand-written
cases are cleaner and better-formed than real input, your system will pass
them, and you will have measured your imagination.

Second trap: a judge that returns an overall 1–10. It returns noise with a
number's confidence.
