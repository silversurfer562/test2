# Documentation staleness audit

**Run:** 2026-09-11 against `attune-ai@5a91b6a`, `attune-rag@f00815d`,
`attune-forms@4191c4e`, `attune-verify@58aedcb`.
**Method:** 20 load-bearing claims from the two authored Phase 1 plans,
re-verified with **all markdown ruled inadmissible as evidence** — only `.py`,
runtime-loaded JSON, workflow YAML and command output counted. Plus six
independent sweeps for distinct classes of staleness.

The synthesis agent hung; this report is assembled from the 28 completed agent
results in the run journal.

---

## The answer: no, staleness did not corrupt the plans

| Verdict | Count |
|---|---|
| confirmed | 11 |
| partly-true | 9 |
| **refuted** | **0** |
| could-not-verify | 0 |

Not one load-bearing premise failed. Every "partly-true" correction attacks a
supporting detail while the conclusion holds — the reviewers' own phrasing
recurs: *"T4 survives intact — do not shrink the plan"*, *"T6 stands"*,
*"T1 survives"*.

The corrections worth carrying into execution:

- **C3** — the price table is in `models/registry.py` (`MODEL_REGISTRY` 125-169,
  `ADDITIONAL_MODELS` 181-214, `TIER_PRICING` 519-526), but the plan's count of
  hand-copied duplicates was wrong. Move boundary unchanged.
- **C2** — a cost row in `thresholds.json` does not "fail cheap, pass expensive";
  it produces an **exit-2 validation error**, because `extract_metrics()`
  hard-codes the metric set. T6 still stands: `check()` has no direction support.
- **C7** — "no `check_thresholds` equivalent in attune-ai" is true by name only.
  `scripts/check_platform_compat.py` already loads a JSON baseline and returns
  a two-list result. T6 remains a port, but there is prior art to mirror.
- **C8** — the eval scripts are unlinted by ruff (`scripts/` is excluded) but
  **are** format-checked by `black --check .`. New tests belong in the existing
  `tests/unit/scripts/` package, not a new one.

**So the plans are safe to execute.** The audit's value is elsewhere.

---

## What it found instead: 74 staleness findings, 22 high severity

| Sweep | Findings | High |
|---|---|---|
| Agent instructions (`CLAUDE.md`, rules, gates) | 20 | 3 |
| Archive dependencies | 12 | 4 |
| Generated-docs drift | 12 | 6 |
| Undated numbers | 12 | 4 |
| Specs describing dead code | 11 | 2 |
| Spec-vs-spec contradictions | 7 | 3 |

### 1. Published numbers that are false — the one that matters most

`attune-rag/README.md` opens with **"Every figure is reproducible with
`attune-rag-benchmark`."** That sentence is false for **three of the six
figures** in the table it introduces.

- The hard-paraphrase headline — *"25% lightweight → 90% transformer"* for
  precision@1, *"25% → 100%"* for recall@3 — **disagrees with your own most
  recent measurement**: `docs/specs/confidence-gated-retrieval/tasks.md` M2
  (measured 2026-08-10, reproducer `scripts/measure_gated_mechanism.py`) on the
  same `corpus_c` hard set.
- The "Quality baselines" table is headed **"Threshold (current)"** and lists
  `precision_at_1 ≥ 0.95` and `mean_faithfulness ≥ 0.9686`. The file CI
  actually feeds to `check_thresholds.py` holds different values. A reviewer
  believes they have two golden queries of slack; the real gate is tighter.
- The faithfulness figures carry **no date and never name the judge model**,
  while README line 507 claims re-measurement "whenever the corpus, judge
  prompt, or harness changes". `thresholds.json` is `measured_at 2026-05-20`.

For a product whose argument is receipts, this is the finding to fix first.

### 2. A user-facing number that is wrong by 5x

`attune-ai/README.md:484` — *"depth budgets run $0.50 / $2.00 / $5.00"*.

`src/attune/models/sdk_errors.py:32` —
`_DEFAULT_BUDGET_USD = {"quick": 2.00, "standard": 10.00, "deep": 25.00}`.

**Someone budgeting a deep run at $5 is uncapped until $25.** Same stale table
in `docs/PROJECT_OVERVIEW.md`.

### 3. A freshness gate that cannot fire

`.github/workflows/help-freshness.yml` runs
`scripts/list_stale_help_features.py`, which computes
`tracked = [name for name, feat in manifest.features.items() if feat.files]`
and returns 0 early when that list is empty. **All 31 features in
`.help/features.yaml` are `status: manual` with no `files:`**, so the list is
always empty and the job is structurally incapable of reporting anything —
over a bundle of **1,287 generated files**.

Meanwhile `attune-rag`'s manifest *can* compute staleness, and **all 14
features are stale** by the project's own hash algorithm. Nothing runs it.

Consequences already visible in the bundle: the plugin documented as `8.9.2`
with 17 skills (actually **16.4.0**, **28 skills**); the MCP surface as
"41 tools in 5 categories" (actually **7 getters**, **66 registered tools**);
a Lite-vs-Full table hardcoded at "Skills 13 / MCP tools 31"; and a warning
file presenting `attune wizard run` as a real command that does not exist.

**These are CI-gated** — `test_projection_drift.py` proves they match their
masters byte-for-byte. The gate checks projection fidelity, not truth.

### 4. Code pointing into the archive

**98 files** across `src/`, `scripts/`, `.github/`, `plugin/`, `attune_redis/`,
`.help/` and `docs/hooks/` reference **40 spec slugs that now exist only under
`docs/specs/archive/`**. Heaviest: `sdk-error-message-fidelity`, cited by 19
files including `src/attune/workflows/base.py` and `src/attune/ops/runner.py`.
This was a full census, not a sample.

Worse, `existing_spec_slugs()` (`elicitation/spec_intake.py:42`) — documented
as the collision check — iterates only the top level of `docs/specs/` and
**never sees the 107 archived directories**. It will tell an agent that
`discovery-sweep` or `lessons-corpus-rag` is available.

And `scripts/phase0/measure.py` writes into
`docs/specs/agent-surface-rebalance/runs/` — a spec whose own archive README
records it as *"Retired — Phase 0 measurement falsified the context-bloat
premise."* Running it recreates a retired spec directory in the live backlog.

### 5. Stale instructions in the files every agent reads

- `.claude/CLAUDE.md` promises a mechanical enforcer: *"`dirty_switch_guard.py`
  — a PreToolUse hook that refuses a branch switch on a dirty tree."*
  `.claude/settings.json` registers it only under the `Edit|Write` matcher,
  **never under `Bash`**. An agent trusts a guard that will not fire on
  `git checkout`.
- `.claude/rules/attune/communication-grammar.md` tells you to add a
  `QuestionType` member to `meta_workflows/models.py`, which only re-exports
  from `attune_forms`.
- `.claude/rules-tail/attune/doc-import-gate.md` says the gate ships
  **advisory** and should be promoted later. `.github/workflows/docs.yml`
  already made it required.

### 6. Two live specs, opposite rulings

`elicitation-form-surface/decisions.md` **D21 (Status: built)** rules that the
widget is default and `AskUserQuestion` the fallback. `host-surface-parity`
**D16/D17** reverse it, and `attune-forms/bridge.py::_route()` follows the
reversal. Both read as governing.

Similarly `safe-abstention-defaults/README.md` says *"executing — next M3, the
bundled-default behavior PR, not shipped"*. `pipeline.py:39` defines
`_BUNDLED_MIN_SCORE = 5.0` and applies it automatically. It shipped.

---

## The structural finding

Every one of these is downstream of one fact: **this repository generates and
archives documentation faster than it verifies it.** 2,964 markdown files;
1,287 generated; 107 archived specs still cited by live code; one freshness
job that cannot fire.

No individual fix addresses that. Two things would:

1. **Point `attune-verify` inward.** It exists to check numeric claims against
   declared truth sources. Every finding in section 1 is exactly its job, and
   it is not run on its own family. This is currently Week 11 of the program —
   on this evidence it should move earlier.
2. **Make `existing_spec_slugs()` see `archive/`** and make the 98 stale
   pointers a checkable rule rather than a discovery. One census script,
   run in CI, and this class stops accumulating.

## Ranked fixes

| # | Fix | Effort | Why |
|---|---|---|---|
| 1 | Correct or remove the three unreproducible README figures | small | A false "every figure is reproducible" is the worst possible claim for this product |
| 2 | Fix the `$0.50/$2/$5` budget table | trivial | Wrong by 5x, user-facing, two files |
| 3 | Make `existing_spec_slugs()` include `archive/` | trivial | Silent slug collisions |
| 4 | Fix or delete `help-freshness.yml` | small | A gate that cannot fire is worse than none |
| 5 | Census the 98 archive pointers; fix or redirect | medium | Full list already produced |
| 6 | Resolve D21 vs D16/D17 and the abstention status | small | Two agents will read them opposite ways |
| 7 | Regenerate the help bundle, or mark it unverified | medium | 1,287 files, several flatly wrong |

## What this audit did not cover

Reproduced from the sweeps' own coverage notes:

- The archive-dependency census is **complete, not sampled** — 98 files / 40
  slugs is a full count. Content-level verification of archived artifacts
  against code expectations was partial.
- The dead-code sweep ran all **240 live spec `.md` files** against a
  whole-repo symbol blob — automated, so it catches renamed and deleted
  symbols but not semantic drift.
- The generated-docs sweep **executed every generator in `--check` mode**
  rather than reasoning about them.
- The undated-numbers sweep read `attune-rag/README.md` in full (690 lines);
  attune-forms and attune-verify were **spot-checked only**.
- The agent-instructions sweep read `.claude/CLAUDE.md` in full (1,338 lines)
  but `coding-standards-index.md` (1,177 lines) only partially.

Nothing here was verified against a running system. All findings are
code-versus-document.
