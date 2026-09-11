# Phase 1 plan files

Drop these into `.claude/plans/` in the target repo and run `/spec`.

| Plan | Slug | Repos | Status |
|---|---|---|---|
| Cost joined to quality | `cost-in-quality-gate` | `attune-rag`, `attune-ai` | **Authored, NOT verified** |
| Temporal staleness | `temporal-staleness` | `attune-ai` | **Authored, NOT verified** |
| Deletion, proven end to end | `provable-deletion` | `attune-rag`, `attune-ai` | Not yet authored |

## Read this before executing

**Neither plan has been through the verification pass.** Three adversarial
lenses were designed for them and none ran — the workflow was interrupted
twice. Specifically, nobody has yet checked that:

- every `path="..."` under `<files-to-modify>` exists, and every one under
  `<files-to-create>` doesn't;
- `read_spec()`'s regexes actually parse the blocks — it is not an XML parser,
  and a stray `<` or a single-quoted attribute drops a task silently;
- each `<check>` is runnable, and at least one is red before the change.

Run `/spec` in review mode and read each task before approving it, or verify
first.

## What the research pass changed

Each plan was authored from a fresh read of the real code, and the readers
were asked to report anything the brief got wrong. They found 40
contradictions across three workstreams. Four of them changed the shape of the
work:

- **attune-rag captures no token counts at all.** `LLMProvider.generate`
  doesn't return usage, so cost cannot be computed from the current call path.
  That prerequisite is T4 of the cost plan, and the brief omitted it entirely.
- **`thresholds.json` is higher-is-better only.** A cost row can't go in as the
  machinery stands — `check_thresholds` needs a direction. That's T6.
- **`attune-ai` has no thresholds file and no `check_thresholds` equivalent.**
  "Wire it in like precision" was wrong; the gate has to be ported from the
  sibling package first. That's T6 of the staleness plan.
- **Age never reaches the model-facing envelope.** `PersonalMemory.query()`
  doesn't carry it, which makes conflict presentation undecidable today rather
  than merely unimplemented. That's T3, and it's a prerequisite, not a feature.

Trust the plans over anything written about these workstreams in
`PROGRAM.md` or `docs/attune-hardening.md` — those were written from an
earlier, shallower read.
