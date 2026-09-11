# System design brief: [system]

Target length: 4–6 pages. If it's longer, it's probably describing the
implementation rather than defending the design.

## 1. The problem

What this system is for, and what specifically makes it hard. Scale, latency
budget, correctness bar, cost ceiling — the constraints that eliminate the
obvious answers.

## 2. Non-goals

What this explicitly does not do. Reviewers attack scope first; settle it up
front.

## 3. Architecture

The diagram, then the walkthrough. For an AI system, show explicitly:

- **Context flow** — what reaches the model, in what order, at what token cost
- **Control flow** — where the model decides and where code decides, marked
  clearly. The boundary between them is the architecture
- **Memory** — read path and write path drawn separately
- **Trust boundaries** — where untrusted content enters, what it can reach,
  what requires human approval

## 4. Alternatives rejected

The section that carries the brief. For each: what it was, why not, and the
measurement. Link the eval runs.

## 5. Failure modes

From your Week 3 taxonomy, not from imagination. For each of the top five:
frequency, cost, current mitigation, residual risk.

## 6. The numbers

| | Value | Measured |
|---|---|---|
| Task success rate | | (date, n, spread) |
| Cost per successful task | | |
| p50 / p95 latency | | |
| Memory write precision | | |
| Deletion test | pass / fail | |

## 7. What I would change with another quarter

Ranked. This is where reviewers learn whether you know your own design's
weaknesses better than they do — which is the actual test.

## 8. Open questions

Things you don't know. Listing them is strength; a brief with no open
questions reads as one that hasn't been stress-tested.
