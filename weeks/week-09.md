# Week 9 — The write path decides memory quality

**The question:** How much of what you store is worth storing?

## Build

Implement the write path from Week 8's design:

1. **Extraction** — what's worth remembering from a session. Be aggressive
   about rejecting. Most turns contain nothing durable.
2. **Deduplication** — near-duplicate detection before write, not after. A
   memory store that accumulates seven phrasings of the same fact will surface
   all seven and crowd out everything else.
3. **Conflict resolution** — when a new memory contradicts an old one, you
   need a policy: supersede with history retained, keep both with timestamps,
   or flag for confirmation. Last-writer-wins loses information you will want
   back, and losing it silently is the worst version.
4. **Provenance** — every memory carries source, timestamp, and confidence.
   Non-negotiable. Without provenance you cannot do Week 10's staleness work,
   and you cannot answer "why does it think that?"
5. **Decay** — an explicit policy per memory type. What expires, what
   consolidates, what is permanent.

## Study (3h)

Kleppmann DDIA ch. 5 on conflict resolution; a recent survey on memory in LLM
agents — search for one from the last year, and read it to argue with rather
than adopt.

## Gate

**Memory precision, measured.** Sample 100 stored memories. Hand-label each:
correct and useful / redundant / wrong. Report the three rates.

Then improve the write path and re-measure on a fresh sample. Report both
numbers. An improvement you can't show as a before and after is a belief.

## Write

`log/week-09.md` with both measurements and what changed between them.

## The trap

Storing every turn because storage is cheap. Storage *is* cheap. Retrieval
contamination is not — every low-value memory competes for a slot in a fixed
token budget at read time, and the cost lands somewhere you won't connect back
to this decision.
