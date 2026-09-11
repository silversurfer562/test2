# Week 4 — Workflow vs agent

**The question:** Which parts of your system should *not* be an agent?

## Build

Pick one feature currently implemented as an agent loop. Build it a second
time as a fixed pipeline — deterministic steps, no model-chosen control flow,
models used only where judgment is genuinely required.

Then run both against the Week 1 suite.

If the fixed pipeline is obviously impossible for the feature you picked, that
is itself a finding worth writing down — but pick a second feature and try
again, because the intuition about which is which is exactly what this week is
building.

## Study (3h)

Yao et al., "ReAct"; Wei et al., "Chain-of-Thought"; and reread Anthropic's
"Building effective agents" with your Week 1 numbers in hand.

## Gate

A head-to-head table:

| | Pipeline | Agent |
|---|---|---|
| Pass rate (n, spread) | | |
| Cost per successful task | | |
| p50 / p95 latency | | |
| Run-to-run variance | | |
| Failure modes (from Week 3 taxonomy) | | |

Plus a one-line decision naming **the number that decided it**.

Variance is the row people skip and the one that matters most in production.
An agent that averages better while swinging wildly is often the worse product.

## Write

An ADR. Include the conditions that would reverse the decision — "if task
count per request exceeds ~5, revisit" is worth more than the decision itself.

## The trap

Assuming the agent wins. Frequently it doesn't, and it costs several times as
much to lose. The agent's advantage is handling variety you can't enumerate;
if you *can* enumerate the paths, the pipeline is usually cheaper, faster, and
far easier to debug at 2am.
