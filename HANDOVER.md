# Handover

Paste this into a new session. Everything below is pushed to
`silversurfer562/test2`, branch `claude/ai-architecture-mastery-plan-oe9hwb`.

**Read this as leads to verify, not as fact.** The session that wrote it got
two significant things wrong before the evidence corrected it, and said so.
Where it says "verified", a command was run; where it says "claimed", it was
not. That distinction is the whole point of the work below.

---

## Who you are working with

Patrick Roebuck, building the **attune** family — `attune-ai`, `attune-rag`,
`attune-forms`, `attune-verify` under the `Smart-AI-Memory` org, plus
`silversurfer562/attune-agent-memory`. Product thesis, in his words: *memory
decides what a session carries; caching decides what carrying costs.*

**Two constraints that shape how to work with him right now:**

1. **He is recovering from hand surgery.** Typing is painful; he can use a
   mouse and short one-handed typing, and is trialling dictation. Ask
   questions with clickable options or answerable in one word. Never make him
   type a path or an identifier — describe approximately, and resolve exact
   names yourself. His own ratified convention (in
   `attune-agent-memory/communication-clarity/decision.md`) is: restate his
   message in the same turn, correct dictation damage while preserving intent
   and voice, then **act without waiting for confirmation**. His escape words
   are **verbatim** and **pause**. When he says **draft**, he is dictating
   prose to publish — then fix transcription only and keep his sentence
   shapes, because that is where his voice lives.
2. **His API credits are exhausted until after the 16th.** He is fine using
   the Claude subscription for sessions. Do not run anything that makes a paid
   model API call in his repos: no `pytest -m llm`, no `--with-faithfulness`,
   no benchmark path that needs `ANTHROPIC_API_KEY`.

---

## The one thing to know before touching `attune-ai`

**Do not run bare `ruff check .`.** `pyproject.toml:508` sets `fix = true`, so
`ruff check` **rewrites your working tree**. Use `ruff check --no-fix .`.

This was the day's most useful finding, and it bit the previous session first.

---

## What is done

**Three verified `/spec` plan files** for Phase 1, in `plans/`. Authored
against the real code, then checked by three adversarial lenses (ground truth,
`read_spec()` regex conformance, does-the-gate-bite) and repaired: 116 defects
found, 19 blocking.

- `cost-in-quality-gate.md` — 8 tasks, clean
- `temporal-staleness.md` — 8 tasks, clean
- `provable-deletion.md` — 9 tasks, **do not execute**, see Blocked below

**A documentation staleness audit** — `docs/staleness-audit.md`. 74 findings,
22 high severity. Headline: `attune-rag/README.md` claims *"Every figure is
reproducible with attune-rag-benchmark"* and that is **false for three of six
figures**, with the hard-paraphrase numbers contradicting the repo's own
2026-08-10 measurement.

**A session-extraction script** — `experiments/extract_sessions.py`. Read-only.
Builds a labelling sheet from Claude Code transcripts for an experiment on
whether retrieval quality predicts session quality. Run `--discover` first.

**Three code fixes**, all in `attune-ai`, all for the same failure shape —
*the safe-looking action does something else and does not say so*:

| Fix | Status |
|---|---|
| CI `ruff check` → `--no-fix` | **landed** on branch `fix/ci-ruff-no-fix` |
| `_portable_path` accepts paths that resolve nowhere | patch written and verified; a session is landing it |
| `read_spec()` drops malformed content in silence | same patch |

The second and third took three attempts to get right. **The contract is in
the patch's docstrings — read them before altering the check.** Requiring the
file to exist fails 9 tests; requiring the parent fails 6; requiring only the
first path segment passes all 173.

---

## What is in flight

| | State |
|---|---|
| Session: Grammar required-slot binding gate (`attune-forms`) | design conversation, no code, waiting on him |
| Session: two silent-failure fixes (`attune-ai`) | landing on `fix/ci-ruff-no-fix` |
| Workflow: `provable-deletion` split | **hung** at 1 of 3 checks |
| Workflow: staleness audit | **hung** on synthesis; results already extracted into the report |

Two workflows hung after hours with no progress. Their per-agent results
survive in `journal.jsonl` under the run directory and can be extracted
without re-running — that is how the audit report was assembled.

---

## What is blocked

`plans/provable-deletion.md` spans `attune-rag` and `attune-ai` and prefixed
every path with the repo name. That resolves to nothing from either repo root
**and fails silently** — the path contains no `..`, so `_portable_path`
accepts it and the executor writes to the wrong location.

`_portable_path` rejects `..`, so neither a `../other-repo/` path nor a repo
prefix works. **One plan file per repo is the only shape `/spec` executes
correctly.** The family's own precedent is
`attune-ai/.claude/plans/extended-cache-ttl-siblings.md` — *"separate repo,
separate PR, do not start in the attune-ai session."*

The split into `provable-deletion` (attune-rag) + `curated-erasure`
(attune-ai) needs redoing.

---

## Corrections the previous session had to make

Carry these forward; they are the reason to distrust confident summaries.

1. **The first capability baseline was wrong by two rubric levels.** Written
   from three repos that turned out to be the weakest sample of his work, it
   concluded "nothing anywhere measures output quality". Reading the four
   attune product repos showed measurement at level 4, not 2: held-out unseen
   corpora, difficulty stratification, CI gates that exit 1, a pre-committed
   go/no-go matrix, a judge that decomposes answers into atomic claims. Tool
   design likewise 4, not 1.
2. **The corrected finding is that the practice is uneven, not behind.** Every
   fix recommended for the weaker repos already existed inside the attune
   family. It is a propagation problem.
3. **An effort estimate of "three lines" took three wrong guesses** about a
   contract that was written down in a test fixture the whole time.
4. **A proposed experiment was circular** — it needed session-outcome data that
   the week of work it was meant to justify would produce.

---

## Where the work lives

```
PROGRAM.md                 the plan being run: 12 weeks, each landing as a
                           shipped change to a named attune package
PHASE-1.md                 the narrowed first phase — three claims
docs/baseline-week-00.md   corrected capability read across seven repos
docs/staleness-audit.md    74 findings, 22 high
plans/                     the three /spec plan files + their status
templates/                 requirements checklist, ADR, eval spec, design brief
experiments/               the session-extraction script
```

`PLAN.md` and `weeks/` are a generic template `PROGRAM.md` was derived from —
keep for re-running the method elsewhere, do not work from them.

**The previous session's own pushback, which he agreed with:** seven documents
were produced about work not yet started, and the only merge-ready patch of
the day came from an agent accidentally breaking a repo and the investigation
that followed. The planning-to-shipping ratio is bad. Prefer shipping.

---

## The open question when he returns

He asked whether to point `attune-verify` at its own family now. A first run
was done and answers it concretely:

- Unconfigured, on `attune-rag/README.md`: **FAIL — 35 verified, 2 refuted,
  85 unknown, 122 supported claims.** Both refutations are real dead links to
  an archived spec.
- It caught **none** of the false numeric claims, because `count_sources`
  requires a declared context file and no attune repo has one.
- Two apparent bugs in the tool: prose words extracted as commands
  (`pass --corpus-path`, `optionally --negatives`), and 70% of claims
  unverifiable because the resolver cannot reach the CLIs.

The proposed next step, unstarted: **write the `--context` file first so the
gate goes red on the three false README figures, then correct them.** Red
before, green after.
