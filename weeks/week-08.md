# Week 8 — Memory reference architecture

**The question:** What are the distinct memory systems in your product, and
what is each one's read path and write path?

## Build

No code this week. A reference architecture document another engineer could
implement from.

Cover four memory types as separate systems, each with its own read and write
path — this separation is the week's whole point:

| Type | Holds | Typical write trigger | Typical read trigger |
|---|---|---|---|
| Working | Current task state | Every turn | Every turn |
| Episodic | What happened, when | End of session or event | "What did we do last time?" |
| Semantic | Facts about the user/domain | Extraction, with confirmation | Grounding most requests |
| Procedural | How to do things here | Success on a repeated task | Task match |

For each, specify: what gets written and by what trigger; what's stored
(schema, provenance, confidence, timestamps); how it's retrieved and ranked;
how it decays or expires; how it's deleted; and — the row most designs
omit — **how conflicts between memories are resolved**.

Then draw it. One diagram, read path and write path visibly separate.

## Study (3h)

Packer et al., "MemGPT" for the paging model; Park et al., "Generative Agents"
for the recency × importance × relevance retrieval score; Wang et al.,
"Voyager" for the skill library as procedural memory.

## Gate

The document and diagram, **reviewed by another engineer** who can ask
questions you can't answer. Record the questions you couldn't answer — that
list is Week 9 and 10's agenda.

## Write

The reference architecture itself. Use `templates/system-design-brief.md`.

## The trap

One vector store called "memory," doing all four jobs badly. The failure is
not that it doesn't work — it works acceptably for a while, then degrades in a
way nobody can diagnose, because four different retrieval problems with four
different decay profiles are sharing one ranking function.
