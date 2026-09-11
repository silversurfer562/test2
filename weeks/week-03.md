# Week 3 — Failure taxonomy

**The question:** What are the top five ways your system fails, ranked by
frequency × cost?

## Build

1. Tracing over the full agent loop — spans for each model call, each tool
   call, each retrieval. Capture inputs, outputs, token counts, latency,
   errors. If you can't reconstruct a session from the trace alone, it isn't
   done.
2. Collect ~100 failing sessions. Read them **by hand**. All of them. This is
   the week's real work and there is no shortcut that preserves the value.
3. Label each with a failure category. Let categories emerge from the traces
   rather than starting from a list.
4. Rank by frequency × cost, where cost includes wasted tokens, latency, and
   damage to the user's trust.
5. For each of the top five, write a hypothesis about its **architectural**
   cause — not its prompt cause.

## Study (3h)

Shinn et al., "Reflexion"; Kleppmann, DDIA ch. 1 and 8.

## Gate

A ranked failure taxonomy with counts, and for each top-five category:

- What it looks like in a trace (so you can find it again)
- The suspected architectural cause
- Which later week addresses it

## Write

`log/week-03.md` with the taxonomy. This document drives Weeks 4 through 11 —
if Week 5's tool refactor doesn't attack a category on this list, you're
working on the wrong thing.

## The trap

Classifying everything as a prompt problem. Prompts are the most available
lever, so they attract the blame. Most agent failures in practice are context
problems (the model wasn't given what it needed) or control-flow problems
(the loop had no way to recover). A trace tells you which; a hunch doesn't.

## Phase review

End of Phase 1. Before Week 4, answer honestly: **do you trust your own
numbers?** If the eval suite is flaky, the judge uncalibrated, or the traces
incomplete, spend next week fixing it. Everything downstream is a comparison,
and a comparison against an untrustworthy baseline is worse than none — it's
confidently wrong.
