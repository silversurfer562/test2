# Operating rhythm

Twelve weeks at 15–20 hours is roughly 200 hours. That is enough to go deep in
three areas. It is not enough to go deep in eight, so the plan spends the hours
deliberately and this document is how.

## The weekly split

| Hours | Activity | Note |
|---|---|---|
| 9–11 | **Build** | On your real systems. This is where the learning is. |
| 3 | Study | Read the week's sources *before* building, with the extraction question in hand |
| 2–3 | Measure | Run the suite, read failures by hand, update the scorecard |
| 1 | Write | The week's ADR or design note |
| 1 | Review | Weekly review template, and next week's gate read in advance |

The build:study ratio is deliberately lopsided. You are not short of exposure
to ideas about AI systems — you're short of decisions made with numbers
attached. Reading more is the comfortable substitute for that and it should be
resisted.

## The daily shape

Two kinds of session, and don't mix them:

- **Deep sessions** (2–4 hours, 3–4 per week) — build and measure. No reading,
  no Slack. The eval suite runs at the end of every one.
- **Short sessions** (45–60 min) — read a paper with a question, or write the
  ADR, or label failure traces. These survive a bad week; deep sessions don't.

## Read with an extraction question

Every source in `docs/reading-list.md` has a question attached. Read for that
question, write two or three sentences answering it in your log, stop. A paper
you read without a question is a paper you'll need to read again.

## When a week goes wrong

It will — not every week, but three or four of the twelve.

**If you're short on hours:** do the gate, skip the reading. The gate is the
week; the reading supports it. Reversing this is the most common way these
programs quietly become book clubs.

**If you miss a gate entirely:** do not roll forward on both tracks. The
phases are dependency-ordered and Weeks 8–11 are close to worthless without
the Week 1 harness. Take the following week to finish the gate, and cut
Week 6 (multi-agent) or Week 11 (fine-tuning) from the program — in that
order. Both are valuable; neither is load-bearing for the rest.

**If a build turns out much bigger than the week:** shrink the scope, not the
gate. One feature instead of the system. One memory type instead of four. The
gate exists to force a measured comparison, and a measured comparison on a
small surface still teaches the thing.

## The log

`log/` is the actual record — not a journal, a lab notebook. Per week:

- The scorecard numbers, with n and spread
- Decisions made, and what would reverse them
- What you expected before the measurement, and what happened

That third line is the one with the most value in it, and the easiest to skip.
Write the prediction down *before* you run the eval. Being wrong on the record
is the mechanism; the rest is bookkeeping.

## Cadence checkpoints

| When | Do |
|---|---|
| Week 0 | Score the rubric, schedule the hours, pick the target systems |
| Week 3 end | Phase review — is the instrumentation actually trustworthy? |
| Week 6 | Re-score the rubric. Expect at least one dimension to go *down* |
| Week 7 end | Phase review — cut Week 6 or 11 now if you're behind |
| Week 10 end | Phase review — is the memory eval measuring across sessions, honestly? |
| Week 12 | Re-score the rubric, run the design review, write the retrospective |
