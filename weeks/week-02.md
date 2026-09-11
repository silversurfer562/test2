# Week 2 — Context as a budget

**The question:** Where do your tokens actually go, and what would you cut first?

## Build

1. Instrument a per-turn context breakdown for a representative task:
   system prompt / tool definitions / retrieved memory or documents /
   conversation history / output. Absolute tokens and percentages.
2. Measure your **prompt cache hit rate**. Then read your provider's caching
   docs and find what's invalidating the prefix — usually something dynamic
   near the front, like a timestamp or a per-request ID.
3. Reorder context so the stable material is at the front and the volatile
   material at the back. Re-measure the hit rate.
4. Now cut. Target a 30% context reduction. Rerun the Week 1 suite after
   every cut.

## Study (3h)

Liu et al., "Lost in the Middle" — and test whether it still reproduces on
your current model; Anthropic on context engineering; your provider's caching
documentation.

## Gate

- A token-spend table by category for one representative task
- Cache hit rate before and after reordering
- **30% fewer context tokens with no eval regression beyond the noise floor**
  — or a written explanation of what the remaining tokens buy, with the eval
  delta that proves it

The second outcome is a pass. "I couldn't cut it, and here's the measurement
showing why" is a real result. "I cut it and it feels fine" is not.

## Write

An ADR (`templates/adr.md`) on your context budget: the allocation, the
ordering rule, and what you'd sacrifice first under pressure.

## The trap

Trimming the prompt and declaring victory without rerunning the suite. Context
cuts fail silently — the system still answers, just slightly worse, on cases
you weren't looking at. This is exactly what Week 1 exists to catch.
