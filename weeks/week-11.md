# Week 11 — Earn the fine-tune

**The question:** For one narrow subtask, can a small model match the frontier
model at a fraction of the cost?

## Build

1. **Pick the subtask.** Narrow, high-volume, judgment-light: routing,
   classification, structured extraction, a rerank step. Not "the whole agent."
   The narrower the task, the better this works — which is the finding.
2. **Harvest training data from your own traces.** You have been logging
   inputs and frontier-model outputs since Week 3. That is a distillation set.
   Clean it, hold out a test split that overlaps nothing in training.
3. **Establish two baselines first**: the frontier model's score on this
   subtask, and a small model *prompted* on this subtask. Fine-tuning that
   fails to beat a well-prompted small model is a real and common outcome, and
   you want to find out cheaply.
4. **Fine-tune** with LoRA or QLoRA. Start small on rank and data volume, and
   add only if the curve says to.
5. **Evaluate all three** on the held-out split.

## Study (3h)

Hu et al., "LoRA"; Dettmers et al., "QLoRA" for the memory math; Hinton et al.
on distillation — your build is this paper with your own traces as the
transfer set; Hoffmann et al., Chinchilla, for data-vs-parameters intuition.

## Gate

A decision table:

| | Frontier | Small, prompted | Small, fine-tuned |
|---|---|---|---|
| Quality on held-out split | | | |
| Cost per 1k calls | | | |
| p95 latency | | | |
| Operational burden | | | |

Plus **an ADR that says ship or don't ship, with the reason.** "Don't ship"
is a perfectly good outcome here and is frequently the right one — the
operational cost of owning a model is real and rarely counted honestly in the
enthusiasm of a good eval result. Count it.

## Write

The ADR, including what would change the decision later: volume thresholds,
price changes, a quality bar moving.

## The trap

Fine-tuning before you have an eval for the subtask. You will produce a model
and have no way to know whether it's better. This week is only possible
because Week 1 happened.

Second trap: skipping the prompted-small-model baseline. It's the cheapest of
the three options and it wins more often than the fine-tuning literature
suggests.

## If you are behind

Second week to cut, after Week 6. See `docs/operating-rhythm.md`.
