# Week 6 — Delegation costs context

**The question:** When does a subagent actually pay for itself?

## Build

1. Take one task with separable parts. Build an orchestrator-worker version:
   a lead that decomposes and delegates, workers with isolated context.
2. Measure the **handoff cost** precisely — tokens spent re-establishing
   context in each worker, plus tokens spent returning results. This is the
   hidden bill, and it scales with the number of workers.
3. Compare against the inline version on quality, total tokens, and wall-clock.
4. Find the crossover point: at what task size or fan-out does delegation win?

## Study (3h)

Anthropic's "How we built our multi-agent research system"; Park et al.,
"Generative Agents" — read the reflection loop, which is also your Week 8
warm-up.

## Gate

A cost model for your system:

- Tokens per subagent call, broken into handoff vs. work
- Wall-clock saving from parallelism, if any
- Quality delta
- **A written rule**: "delegate when ___, don't when ___"

## Write

An ADR on your delegation policy.

## The trap

Parallelism that duplicates context N times. Four workers each needing the
same 8k of background is 32k of tokens to save some seconds. Sometimes that's
worth it — read-heavy research tasks often are. Write tasks that need shared
state usually are not, because the coordination cost compounds.

## If you are behind

This is the first week to cut. See `docs/operating-rhythm.md`.
