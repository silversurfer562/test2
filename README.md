# AI Architecture Mastery — a 12-week program

You already ship AI systems. This is not a course in what an LLM is.

The distance between *my system works* and *I can defend this design under
questioning* is not more reading. It is measurement, and the willingness to
write down the alternative you rejected and why. Everything here is built
around that.

**Every week ends with a number, not a feeling.** If a week's gate can't be
checked by someone else running your harness, the week didn't happen.

## What this program assumes

| | |
|---|---|
| Starting point | Already running AI systems in production |
| Focus | Agentic + memory architecture, and the model layer |
| Budget | ~15–20 hrs/week for 12 weeks (~200 hours) |
| Substrate | Your real systems — not toy projects |

That last row matters most. Every build task below is written to be done
*on something you already own*. A throwaway demo can't teach architecture,
because architecture is the set of decisions that only hurt at scale, under
load, over time, with real data.

## The shape of it

| Phase | Weeks | You come out able to |
|---|---|---|
| Instrumentation | 1–3 | State your system's quality, cost, and failure modes as defensible numbers |
| Agentic architecture | 4–7 | Decide *where* an agent belongs, design its tools, and keep it alive through failure |
| Memory architecture | 8–10 | Design a memory layer with separate read and write paths, and prove its quality over time |
| Model layer | 11 | Decide fine-tune vs. prompt vs. retrieve, with a cost/quality table behind it |
| Synthesis | 12 | Defend the whole architecture in a review and survive it |

## Repo layout

```
PLAN.md                  The full 12-week program, week by week
docs/
  baseline-week-00.md    Your week-0 baseline, read from three repos — start here
  capability-rubric.md   Ten dimensions, four levels — score yourself at weeks 0, 6, 12
  evaluation-playbook.md The central discipline: how to measure agents and memory
  operating-rhythm.md    Weekly time split, and what to do when a week goes wrong
  reading-list.md        Sources by week, with what to extract from each
weeks/week-NN.md         One file per week: question, build, study, gate, trap
templates/               ADR, eval spec, weekly review, system design brief
projects/                The three capstone builds that run through the 12 weeks
log/                     Your working log — the record of what you actually did
```

## Start here

1. Read `docs/baseline-week-00.md`. It scores you against the rubric from
   evidence in `attune-agent-memory`, `memdocs`, and `deep-study-ai` — with
   your role in each weighted — and it **reweights the twelve weeks**. The
   short version: you are past the generic Weeks 8 and 9, no system you own
   gives a model tools, and nothing anywhere measures output quality. Correct
   the scores where the read is wrong; it sees three repos at one commit each
   and nothing unpushed.
2. Save your corrected scores as `log/rubric-week-00.md`. You need the before
   picture and you will not be able to reconstruct it in December.
3. Read `docs/operating-rhythm.md` and put the hours in your calendar. Hours
   that aren't scheduled aren't budgeted.
4. Open `weeks/week-01.md` — and read it against the baseline's Week 1 row.
   Your version is *lift the existing harness to task level*, not *build one*.

## How to use the gates

Each week has a **gate** — a pass condition stated as something checkable.
The gate is the point. Reading the papers without passing the gate is
entertainment.

You will miss gates. When you do, don't roll forward and hope: the phases
are dependency-ordered, and Weeks 8–11 are close to worthless without the
eval harness from Week 1. `docs/operating-rhythm.md` has the recovery rule.
