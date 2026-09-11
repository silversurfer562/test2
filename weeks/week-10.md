# Week 10 — Stale memory is worse than no memory

**The question:** What does your system do when a memory is true-but-outdated?

## Build

1. **Retrieval under budget.** Fix a realistic token budget for memory in the
   context window. Everything below is about what wins a slot.
2. **Scoring on three axes** — recency, relevance, importance — combined and
   weighted. Tune the weights against the eval set, not against intuition.
3. **Conflict presentation.** When retrieval returns contradictory memories,
   decide what reaches the model: the most recent only, both with timestamps,
   or an explicit flag. Different answers are right for different domains;
   having no answer is wrong in all of them.
4. **An adversarial eval set.** Build it deliberately:
   - Facts that changed between sessions (user moved, preference reversed)
   - Facts that expired (a deadline now past)
   - Contradictions between two memories of equal confidence
   - Injected content in a stored memory attempting to steer behavior
5. **A deletion test.** Delete a memory. Ask a question only that memory could
   answer. If the answer still appears, your deletion is cosmetic — check
   caches, embeddings, derived summaries, and consolidated memories.

## Study (3h)

Gao et al., RAG survey — skim the taxonomy, dwell on evaluation; reread
"Lost in the Middle" for what ordering does to retrieved *memories*.

## Gate

- Adversarial eval passing at a stated rate: system prefers the current fact,
  or surfaces the conflict, in ≥ X% of cases. Set X before you run it.
- **Deletion test passing**, including derived artifacts. This is a privacy
  commitment, so test it like one.
- Multi-session scenarios in the suite: a fact stated in session 1 and needed
  in session 5.

## Write

An ADR on your memory read policy: budget, weights, conflict rule, and what
would change them.

## The trap

Measuring retrieval recall and calling it memory quality. Recall tells you the
memory *could* be found. It tells you nothing about whether it should have
won a slot, whether it was still true, or whether the older memory sitting
next to it quietly contradicted it.

## Phase review

End of Phase 3. Is your memory eval genuinely measuring across sessions, or
have you built a very good single-session retrieval test and labelled it
memory?
