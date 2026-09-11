# Week 12 — The design review

**The question:** Can you defend the whole thing to someone trying to break it?

## Build

1. **A system design brief** for the full architecture you've worked on —
   use `templates/system-design-brief.md`. The section that carries the weight
   is *alternatives rejected and why*, with the numbers from Weeks 1–11 behind
   each one.
2. **Run a real review.** Find two or three engineers who will actually push
   back — ideally including one who doesn't work on AI systems, because they
   ask the questions your assumptions have stopped raising. Present. Take
   fire. Record every objection.
3. **Answer each objection** in writing: accepted and changed / accepted as a
   known limitation / rejected with reasoning.
4. **Revise `templates/requirements-checklist.md`** from what the quarter
   taught you — add the questions whose absence bit you, cut the ones that
   never earned their 45 minutes.
5. **Re-score the rubric** and write the retrospective.

## Study (3h)

Nygard, "Documenting Architecture Decisions" — one page, and it is the whole
idea; Richards & Ford on trade-off analysis, for how to present a decision so
a reviewer attacks the reasoning rather than the conclusion.

## Gate

- A design brief with alternatives rejected and measurements attached
- **At least three substantive objections recorded and answered.** If the
  review produced no substantive objections, it wasn't a review — find harder
  reviewers and run it again.
- `log/rubric-week-12.md`, scored against the same instrument as week 0
- A revised requirements checklist, with the diff against the week-0 version
  visible — that diff is a compact record of what twelve weeks taught you
- A retrospective: what the numbers changed your mind about

## Write

The retrospective is the most valuable document of the twelve weeks. Structure
it around three questions:

- Which belief did a measurement kill?
- Which decision would you reverse today, and what would it have cost to know
  that in Week 1?
- What do you now refuse to do without an eval?

## The trap

A design doc that lists what you built. Nobody needs it — the code is right
there. A design document earns its length by explaining what you *didn't*
build and what evidence made that the right call. That distinction is the
whole difference between documentation and architecture, and it's the thing
you've spent twelve weeks earning the right to write.

## After Week 12

The rubric will show two or three dimensions still at level 2. Pick one, and
run a four-week version of this same structure against it: baseline, build,
gate, review. The program is a template, not a finish line.
