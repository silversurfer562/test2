# Capability rubric

Ten dimensions. Four levels. Score yourself at week 0, week 6, and week 12,
and save each pass to `log/rubric-week-NN.md`.

Score against **evidence you could show someone**, not against what you
believe you could do. If you cannot point at an artifact — a harness, a doc,
a trace, a PR — you are at the level below.

## The levels

| L | Name | Test |
|---|---|---|
| 1 | Aware | You can describe the concept and name a tool that does it |
| 2 | Applies | You have done it once, on a real system, following someone else's design |
| 3 | Designs | You have chosen between alternatives on cost/quality grounds and written the reasoning down |
| 4 | Sets direction | Others build against your design, and you have changed your own mind on the record when the numbers said so |

Level 3 is the target for most dimensions by Week 12. Level 4 in two or three
is a strong quarter. Level 4 across ten is not achievable in twelve weeks and
claiming it would be the exact failure mode this program exists to fix.

## The dimensions

### 1. Measurement & evaluation
- **L1** — You know what an eval set is.
- **L2** — You run an eval suite someone else built.
- **L3** — You build eval sets from production traces, calibrate an LLM judge against human labels, and report run-to-run variance alongside the score.
- **L4** — You set the quality bar for a system and defend it when it blocks a release.

### 2. Context engineering
- **L1** — You know context windows are finite.
- **L2** — You trim prompts when you hit limits.
- **L3** — You budget context by category, design for cache hit rate, and can say what you'd cut first and what it would cost.
- **L4** — Your context budget is a documented constraint others design within.

### 3. Control flow — workflow vs. agent
- **L1** — You've used an agent framework.
- **L2** — You build agent loops that work.
- **L3** — You decide per-feature whether it should be an agent at all, with a measured comparison behind the decision.
- **L4** — You can look at a proposed feature and predict where the agent will fail, before anyone builds it.

### 4. Tool & interface design
- **L1** — You've written tool definitions.
- **L2** — Your tools work when the model calls them correctly.
- **L3** — You design tool surfaces for a fallible reader: error strings that say what to do next, granularity chosen against measured error rates.
- **L4** — Your tool conventions are adopted across systems you don't own.

### 5. Memory architecture
- **L1** — You know memory is more than a vector store.
- **L2** — You've shipped retrieval over stored conversation history.
- **L3** — You separate working / episodic / semantic / procedural memory, with distinct read and write paths, provenance, and a decay policy.
- **L4** — You can state the failure modes of a memory design from the schema alone.

### 6. Reliability & failure handling
- **L1** — You add retries.
- **L2** — You handle the errors you've seen.
- **L3** — You design for idempotency, checkpointing, and resumption, and you've proven resumption by killing a live run.
- **L4** — You set the reliability contract for a system and the budget to meet it.

### 7. Cost & latency engineering
- **L1** — You know which model is cheaper.
- **L2** — You track spend.
- **L3** — You hold a cost-per-successful-task number, know your p95, and can move along the cost/quality frontier deliberately.
- **L4** — You own the unit economics of an AI product feature.

### 8. Model selection & adaptation
- **L1** — You pick models by reputation.
- **L2** — You A/B two models on your own task.
- **L3** — You decide prompt vs. retrieve vs. fine-tune on measured grounds, and you've shipped (or correctly rejected) a fine-tune.
- **L4** — You set the model strategy — routing, fallbacks, upgrade path — for a product.

### 9. Safety, permissions & data boundaries
- **L1** — You know prompt injection exists.
- **L2** — You sanitize obvious inputs.
- **L3** — You design trust boundaries: what the agent may do unattended, what needs approval, how untrusted content is isolated from privileged tools, how deletion actually deletes.
- **L4** — You define the permission model others implement.

### 10. Communicating architecture
- **L1** — You explain your design verbally.
- **L2** — You write design docs after building.
- **L3** — You write ADRs before building, listing rejected alternatives and the conditions that would reverse the decision.
- **L4** — You run reviews of others' architectures and change outcomes.

## Scoring template

Copy into `log/rubric-week-NN.md`:

```
| Dimension | Score | Evidence (artifact, link, or "none") |
|---|---|---|
| 1. Measurement & evaluation |  |  |
| 2. Context engineering |  |  |
| 3. Control flow |  |  |
| 4. Tool & interface design |  |  |
| 5. Memory architecture |  |  |
| 6. Reliability & failure handling |  |  |
| 7. Cost & latency |  |  |
| 8. Model selection & adaptation |  |  |
| 9. Safety & data boundaries |  |  |
| 10. Communicating architecture |  |  |

Weakest dimension: 
What I'd need to do to move it one level: 
```
