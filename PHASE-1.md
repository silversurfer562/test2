# Phase 1 — Claims

**Five weeks. Three specs. No new features.**

The attune family measures itself better than most products do: held-out
corpora, difficulty stratification, CI gates that exit 1, a package whose job
is checking numeric claims against truth sources. Phase 1 is not about raising
that standard. It's about three places where the family **makes a claim it
cannot currently check**.

That's the whole entry criterion. A gap only belongs in Phase 1 if a customer,
a regulator, or a careful reader could ask *"prove it"* and the answer today is
an argument rather than a command they can run.

## The three

| # | The claim | Why it isn't checkable today | Weeks |
|---|---|---|---|
| 1 | **Carrying context costs what we say** | `benchmark.py` returns precision, recall, and latency. No cost field. `cost_tracker.py` gets price history right and is wired into no benchmark | 1 |
| 2 | **Deleted memory is deleted** | `CorpusProtocol` is read-only by construction. `grep` for `remove\|reindex\|invalidate\|clear` across corpus, retrieval and embedding returns nothing. No removal path, so no removal test | 2–3 |
| 3 | **Stale memory is handled** | The protocol's staleness claim was ratified 2026-07-02. `--phase persistence` proves recall survives *process death*, which is durability, not staleness. `get_stale_patterns()` covers patterns, not facts that changed | 4–5 |

Claim 1 is half your product thesis — *selectivity × economics* — with no
number on the economics side. Claim 2 is the one with a regulatory shadow and
the only one where being wrong costs trust rather than accuracy. Claim 3 is the
load-bearing assertion of the two-layer protocol, reasoned carefully and never
tested.

## What "done" means, identically for all three

A claim moves from asserted to checked when **all four** hold:

1. **A command anyone can run** produces the number. Not a notebook, not a
   procedure — a command in the README.
2. **The number has a date, an n, and a spread.** A figure without those three
   is a screenshot of a belief.
3. **A gate fails on regression**, wired into CI, not into someone's memory.
4. **One check is red before the change and green after.** A test that passes
   on unchanged code proves nothing about the change.

Rule 4 is the one that gets skipped. Write the failing test first on all three.

## Sequencing, and why

Ordered by irreversibility, not by size.

**Claim 1 first** because it's the smallest and it's a dependency: once cost is
a gated field, Claims 2 and 3 can be costed as they land rather than argued
about afterwards.

**Claim 2 second** and it gets two weeks. The invalidation surface is wider
than it looks — the entry token cache is a sidecar that dies with the entry and
costs nothing, but embeddings have their own lifetime, and the alias and
summary override maps will happily keep pointing at a document that no longer
exists. That dangling pointer surfaces as a retrieval error weeks later, in
someone else's code.

**Claim 3 last** because it's the one whose *design* question is still open —
what reaches the model on a conflict: most recent only, both with timestamps,
or an explicit flag. That decision wants the failure evidence the first two
weeks produce.

## Executing with `/spec`

Each claim ships as a plan file in `.claude/plans/`, executed task-by-task
through `/spec` with its quality gates and per-task approval.

Three things worth knowing before you run them:

- **`read_spec()` is regex, not an XML parser.** Task-critical content outside
  a `<task>` block is silently dropped. Single quotes on attributes are
  dropped. A `<file>` without `path="..."` is dropped. The specs are written to
  the parser's exact shapes; keep them that way when you edit.
- **`severity="high"` blocks auto-run.** The runner offers only *Fix and retry*
  or *Acknowledge risk*. It's a real brake, so it's reserved for the risks
  where a human must stop and look — principally deletion touching derived
  artifacts.
- **`<dependencies>` is the execution order**, so it has to be honest. A task
  that can't actually start until another finishes should say so, even when
  that makes the plan look slower.

## The plans

| Plan | Slug | Repos |
|---|---|---|
| Cost joined to quality | `cost-in-quality-gate` | `attune-rag`, price table from `attune-ai` |
| Deletion, proven end to end | `provable-deletion` | `attune-rag`, `attune-ai` |
| Temporal staleness | `temporal-staleness` | `attune-ai` |

Each was authored against the real code and then checked by three adversarial
passes: **ground truth** (does every path and symbol exist where the plan says),
**parser conformance** (will `read_spec()` actually parse it), and **does the
gate bite** (could someone mark this done while the claim stays false).

## What Phase 1 explicitly is not

- **Not a measurement upgrade.** `attune-rag` already publishes numbers on a
  corpus it has never seen or tuned on. Phase 1 adds no rigour there; it
  extends the same rigour to three things currently outside it.
- **Not a fifth harness.** All three extend existing machinery: the locked
  `thresholds.json`, the existing gate workflow, the existing `--phase`
  architecture in `memory_recall_eval.py`.
- **Not the propagation work.** Porting `prompts.py`'s passage fencing to
  `deep-study-ai` is Week 12. It's a one-afternoon fix and it can be done any
  time, but it isn't Phase 1.

## The honest cost

Five weeks shipping no roadmap features. The defence is one sentence: **three
claims the product currently makes on credit get receipts, and one of them is
the kind you don't want to be discovering under a subpoena.**

If that argument doesn't hold for a given week, cut that week. It's meant to be
attackable.
