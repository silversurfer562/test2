# Week 7 — Durable agents

**The question:** What happens when step 7 of 12 fails at 2am?

## Build

1. **Checkpointing.** Persist agent state at each step so a run can resume
   rather than restart. Decide explicitly what's in the checkpoint — full
   message history is the easy answer and the expensive one.
2. **Idempotency.** Every tool with a side effect takes an idempotency key.
   A retry must not double-charge, double-send, or double-write.
3. **Retry policy with a budget.** Not unlimited retries — a token and
   wall-clock budget, with a defined behavior on exhaustion. An agent that
   retries forever is a system that fails slowly instead of fast.
4. **The approval surface.** Which actions run unattended, which need a human.
   Write the boundary down; it's a security decision, not a UX one.
5. **The sandbox boundary.** What the agent can reach. Where untrusted content
   — retrieved documents, tool output, user files — is isolated from
   privileged tools. Prompt injection is a control-flow problem, and it
   belongs in this week.

## Study (3h)

Temporal's documentation on durable execution and idempotency, for the
vocabulary; Kleppmann DDIA ch. 11 on exactly-once as an illusion built from
idempotency plus retries.

## Gate

**Demonstrated resumption.** Kill the process mid-run. Restart. The run
completes with no duplicated side effects. Record it — a terminal capture or
a test in CI.

Plus a one-page trust-boundary document: what runs unattended, what needs
approval, how untrusted content is quarantined.

## Write

An ADR on the reliability contract: what you guarantee, what you don't, and
what it costs.

## The trap

Retries that re-execute non-idempotent writes. It's the single most common
production failure in agent systems, it's invisible in testing because you
test the happy path, and the users find it first.

## Phase review

End of Phase 2. If you're behind, cut Week 6 or Week 11 now rather than
compressing the memory phase — Weeks 8–10 are the core of what you're here
for.
