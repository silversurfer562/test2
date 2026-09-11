# Plan: Temporal staleness

**Spec**: [docs/specs/temporal-staleness/](../../docs/specs/temporal-staleness/)
**Created**: 2026-09-11

---

## Summary

attune can prove a memory survives process death. It cannot prove a memory that went out of date loses the slot it used to win. `scripts/memory_recall_eval.py` has `--phase all|persistence|capture|evaluate`; `run_persistence_benchmark()` forks a capture subprocess and then an evaluate subprocess against one `tempfile.mkdtemp()` root and reads results back through a file. That is durability testing and it is real. It measures nothing about time. The scored metrics in `evaluate()` are `hit_at_1`, `hit_at_3`, and two lists of top-1 scores — every one of them asks "could the right thing be found", none asks "what was sitting above it".

The claim with no test is the two-layer memory protocol ratified 2026-07-02 in `attune-ai-dev/discipline/COLLABORATION_DISCIPLINE.md` §5 (lines ~684-710): stale operational memory is worse than none and its regime is machine verification at load, every time; stale durable memory fails softly and its regime is human review over time. The durable half is shipped — `scripts/review_curated_memory.py` runs the keep/wrong/sharper verdict loop against `src/attune/memory/verdict_log.py`, and `scripts/audit_curated_memory.py` sweeps advisory and exits 0 on purpose. The operational half has no machine verification at load anywhere, and no measurement that would notice its absence.

Three things reading the code changed about the brief, and the plan is built on the code. First, the staleness subsystem already exists: `src/attune/memory/curated_audit.py` is 815 lines with `resolve_age_basis()`, `unverified_age_days(mem, today=...)`, `epistemic_tier()` against `TIER_SETTLED_MAX=10.0` / `TIER_CHECK_MAX=45.0`, and `PersonalMemory.query()` already calls `_annotate_staleness()` on every hit. This plan reuses that model and does not build a second one; the brief's citation of `patterns/confidence.py::get_stale_patterns(days=90)` is about pattern usage recency and is unrelated. Second, `PersonalMemory.capture()` writes through `atomic_write_text`, which does `tmp.replace(path)` — re-capturing the same topic and kind leaves exactly one file, so "fact stated session 1, changed session 3" as the brief describes it has nothing left to lose the slot to. T1 and T3 fixtures must use distinct topic slugs or the scenarios measure nothing. Third, the memory path is not an undefended door: `src/attune/memory/provenance.py` wraps every recalled hit in an untrusted-evidence envelope and `mcp/memory_handlers.py` strips prose so only the envelope reaches the model. The genuine defect next door is that `_stamp_provenance()` builds `context_block` from `hit["excerpt"]` alone, so the age `_annotate_staleness()` computed one line earlier never reaches the model — and `cli_commands/memory_commands.py::cmd_memory_recall` prints `hit["summary"]` and `hit["excerpt"]` raw, with neither envelope nor age.

Shipping this changes one product claim from asserted to measured: that a recalled memory arrives with its age attached, and that when a current fact and a superseded one compete, the report says which one occupied slot 1 and by what margin. It does not change ranking — `docs/specs/memory-status-integrity` D1 (label, never suppress by age) forecloses dropping the stale hit, and this plan does not reopen it. The primary metric is slot occupancy. Recall over the temporal set is reported as a diagnostic and is explicitly not a pass condition, because a run where every current fact is findable at k=3 while the superseded one wins slot 1 every time is a failing run, and T5 makes the report say so rather than warning about it in a comment.

---

## Tasks

<task id="T1" name="Spec home, ruled semantics, pre-committed matrix">
  <objective>
    Create the spec home and rule the four semantic questions before any code exists, so none of them get settled by accident during implementation. Decide and record: (a) the work lives in a new docs/specs/temporal-staleness/ rather than extending memory-recall-eval, because spec-status-reminder.yml and the changelog gate both key off a directory name and the recall spec is closed; (b) T1 and T3 scenarios use DISTINCT topic slugs, because capture() replaces root/TOPIC/KIND.md destructively and a same-slug re-capture leaves no competitor; (c) simulated sessions are aged with os.utime, because _build_skeleton() writes no frontmatter, load_memory() therefore returns verified=None, and resolve_age_basis() falls to the "mtime" basis at DEFAULT_VOLATILITY 0.75; (d) the primary metric is slot-1 occupancy, and hit@k over the temporal set is a stated non-metric. Write D1 as a PRE-COMMITTED matrix naming the specific must-pass cases by id, never a percentage.
  </objective>
  <files-to-create>
    <file path="docs/specs/temporal-staleness/requirements.md">Status line, Problem, Goal, Approach, Requirements as "- **R1 - Title.**" bullets, Non-goals, Done when. R1 isolation (explicit tmp roots only), R2 realistic scenario content, R3 hand-authored ground truth not derived from the system under test, R4 slot occupancy as the primary metric, R5 one clean report, R6 no second age model.</file>
    <file path="docs/specs/temporal-staleness/design.md">Architecture as an ASCII text block showing the temporal phase orchestrating two leaf subprocesses. OQ1 scenario slug shape, OQ2 session forgery mechanism, OQ3 conflict presentation, OQ4 gate shape, each with lettered options and a RECOMMENDED marker. Mirrors docs/specs/memory-recall-eval/design.md.</file>
    <file path="docs/specs/temporal-staleness/decisions.md">D1 headed "D1 - Temporal go/no-go matrix (PRE-COMMITTED 2026-09-11)" with a Result/Decision table, the sentence "The commit timestamp is the arbiter", and the ams-int8-quantization clause "Numbers revisitable only with stated reason before the run, never after". Names every must-pass case id before any case runs.</file>
  </files-to-create>
  <files-to-modify>
    <file path="docs/specs/memory-recall-eval/design.md">Add one line to the Architecture block recording that scripts/memory_recall_eval.py, not the spec-named scripts/eval_personal_memory_recall.py, carries the multi-process phase architecture and is therefore where the temporal phase lands. Reconciles the two harnesses in writing instead of leaving the split undocumented.</file>
  </files-to-modify>
  <validation>
    <check>ls docs/specs/temporal-staleness/ lists requirements.md, design.md and decisions.md, and each opens with a "**Status:**" line carrying a date.</check>
    <check>grep -nE "[0-9]+%|rate" docs/specs/temporal-staleness/decisions.md shows no pass condition expressed as a percentage; the D1 table rows name case ids.</check>
    <check>grep -n "hit@" docs/specs/temporal-staleness/requirements.md shows hit@k appearing only under Non-goals.</check>
    <check>git log -1 --format=%cI on the decisions.md commit predates the first commit touching scripts/memory_recall_eval.py in this branch.</check>
  </validation>
  <risks>
    <risk severity="medium">Writing D1 as a rate over four scenario classes repeats the error the 2026-08-28 memory-recall-eval entry names explicitly ("2 of 6 must NOT be read as a 33% false-positive rate ... the Wilson interval is roughly 4%-78%"). The matrix must be a named per-case table.</risk>
    <risk severity="medium">Choosing a new spec directory splits memory-eval history across two homes. Mitigated by the cross-reference line added to memory-recall-eval/design.md.</risk>
  </risks>
</task>

<task id="T2" name="Temporal fixture with expected winners and ages">
  <objective>
    Author TEMPORAL_SCENARIOS as a hand-written data table beside the existing CORPUS and QUERIES in scripts/memory_recall_eval.py. Each scenario carries a list of captures (topic, kind, content, session_index), a per-capture age in days used to drive os.utime, the query text, the topic that MUST occupy slot 1, and the topic(s) that must not. Four classes. T1-changed: a fact under one topic at session 1, a superseding fact under a DIFFERENT topic at session 3, queried at session 5. T2-expired: a deadline or status whose date has passed. T3-contradiction: two topics with incompatible claims and deliberately matched keyword overlap, so the scores tie and the tiebreak is what is being measured. T4-injected: two sub-cases, one high-signal payload (role-delimiter or tool-invocation shaped) that MUST carry an instruction flag on every tier, and one bare curated imperative that MUST NOT flag, because _DIRECTIVE_PATTERNS apply only to UNTRUSTED_TIERS and _stamp_provenance stamps tier="curated". Add a fixture-vs-corpus cross-check that runs before any scoring and exits nonzero on drift.
  </objective>
  <files-to-modify>
    <file path="scripts/memory_recall_eval.py">Add a TemporalCapture and TemporalScenario dataclass pair and the TEMPORAL_SCENARIOS table after QUERIES. Add check_temporal_fixture() which verifies every expected-winner and must-not-win topic appears in the scenario's own capture list and that every topic slug is unique within a scenario, returning a nonzero exit before any number is printed, mirroring scripts/phase0/lessons_rag_benchmark.py.</file>
  </files-to-modify>
  <validation>
    <check>python -c "import importlib.util,sys;s=importlib.util.spec_from_file_location('m','scripts/memory_recall_eval.py');m=importlib.util.module_from_spec(s);sys.modules['m']=m;s.loader.exec_module(m);print(len(m.TEMPORAL_SCENARIOS))" prints a count of at least 5 and the four class prefixes t1/t2/t3/t4 each appear at least once. RED before this change (AttributeError), GREEN after.</check>
    <check>Every scenario's expected_winner differs from at least one must_not_win topic in the same scenario, and no scenario captures the same (topic, kind) pair twice — assertable by reading the table, and pinned by the test in T7.</check>
    <check>Temporarily edit one scenario's expected_winner to a topic it does not capture; the run exits nonzero and prints no metrics. Revert.</check>
  </validation>
  <risks>
    <risk severity="medium">Hand-matching keyword overlap for T3 so the scores actually tie is fiddly against an unbounded overlap count. If they do not tie, the scenario measures ranking, not tiebreaking; record the observed margin rather than tuning the fixture until it produces the wanted answer.</risk>
    <risk severity="low">Scenario prose that trips _secret_gate would be redacted before it reaches disk. Keep content free of anything shaped like a credential.</risk>
  </risks>
  <dependencies>
    <dep>T1</dep>
  </dependencies>
</task>

<task id="T3" name="Carry age into the model-facing envelope">
  <objective>
    Fix the concrete defect that makes conflict presentation undecidable today. In PersonalMemory.query(), _annotate_staleness() stamps unverified_days, staleness and status onto each hit; _stamp_provenance() then runs and builds context_block from hit["excerpt"] alone, and wrap_recalled() has no parameter for age. The MCP handler returns that context_block as the model-facing "context" and strips summary and excerpt from the structured results, so the model receives prose with no age in one field and age with no prose in another. Add an optional status/age argument to wrap_recalled(), thread it through provenance_fields() and _stamp_provenance(), and implement the ruled presentation: both conflicting memories reach the model, each labelled with its own age and epistemic tier, in the order query() already produced. Do not drop or reorder by age — memory-status-integrity D1 forecloses that. Secondary: bring cmd_memory_recall's human path into line, or record in decisions.md why the CLI stays raw.
  </objective>
  <files-to-modify>
    <file path="src/attune/memory/provenance.py">wrap_recalled() gains a keyword-only status argument (the format_status_annotation string, or None). When present it renders inside the recalled_memory envelope as an explicit age line. provenance_fields() gains the same pass-through so context_block carries it. Docstrings cite docs/specs/temporal-staleness R4.</file>
    <file path="src/attune/memory/personal.py">_stamp_provenance() reads hit["status"] and hit["unverified_days"] (already stamped by _annotate_staleness, which runs first at line 310) and passes them into provenance_fields(). Keep the narrow (KeyError, TypeError, ValueError) handler and the label-never-reorder posture.</file>
    <file path="src/attune/cli_commands/memory_commands.py">cmd_memory_recall's human path prints hit["summary"] and hit["excerpt"] raw. Print the staleness/status label alongside them so the human surface and the MCP surface agree about what a recalled memory looks like.</file>
    <file path="src/attune/mcp/memory_handlers.py">_handle_personal_memory_recall keeps stripping summary and excerpt; confirm the context it returns now carries the age, and leave the fail-closed ImportError branch untouched.</file>
    <file path="tests/unit/memory/test_provenance.py">Add cases for the status argument. Keep the module's stated posture: assert framing and labelling, never that a payload is neutralised.</file>
    <file path="tests/unit/memory/test_personal_memory.py">Pin that a hit's provenance context_block contains the same status string that _annotate_staleness stamped on the hit.</file>
  </files-to-modify>
  <validation>
    <check>python -c "import inspect,sys;sys.path.insert(0,'src');from attune.memory.provenance import wrap_recalled;assert 'status' in inspect.signature(wrap_recalled).parameters" exits 0. RED before this change, GREEN after.</check>
    <check>python -m pytest tests/unit/memory/test_provenance.py tests/unit/memory/test_personal_memory.py -q passes.</check>
    <check>Capture one memory into a tmp root, query it, and assert hit["provenance"]["context_block"] contains hit["status"] — RED before, GREEN after.</check>
    <check>ANTHROPIC_API_KEY="" attune memory recall "redis timeout" prints a staleness label on each result line.</check>
  </validation>
  <risks>
    <risk severity="high">render_recall_for_context() is documented in-code as "the R1 boundary - the CONSUMER CONTRACT" and its live consumer is plugin/hooks/session_recall.py::_format. Changing the envelope text changes what every session injects. A human should read the rendered before/after side by side before this merges.</risk>
    <risk severity="medium">Adding an age line lengthens every envelope and consumes context on every recall. Measure the added characters per hit and state the number in decisions.md rather than asserting it is small.</risk>
    <risk severity="medium">The status label is computed from file mtime for captured personal memories (no frontmatter, so resolve_age_basis returns the "mtime" basis). The envelope must not imply the claim was verified on that date. Render the basis, not just the date.</risk>
  </risks>
  <dependencies>
    <dep>T1</dep>
  </dependencies>
</task>

<task id="T4" name="--phase temporal on the existing multi-process architecture">
  <objective>
    Add "temporal" to the --phase choices in scripts/memory_recall_eval.py by mirroring run_persistence_benchmark(), not by writing a second harness. A tmp root under tempfile.mkdtemp(), a capture-side subprocess that writes the scenario captures and applies os.utime per each capture's session age, then a separate evaluate-side subprocess starting from a brand-new PersonalMemory against the same on-disk root, with results handed back through --json-out to a FILE — never stdout, because attune_rag's structlog PrintLogger writes there and corrupts inline JSON, as the existing code documents at run_persistence_benchmark. Reuse --root. Add --scenario-set so the capture and evaluate leaf phases know which fixture to run while keeping their existing corpus behaviour unchanged by default. Fix the module docstring's "~/.attune/personal_memory" to the real default "~/.attune/memory" (src/attune/memory/personal.py line 32) in the same commit. Extend print_report() with a temporal block.
  </objective>
  <files-to-modify>
    <file path="scripts/memory_recall_eval.py">Add capture_temporal(global_root), evaluate_temporal(global_root) and run_temporal_benchmark(); add "temporal" to the --phase choices and --scenario-set to the parser; extend main()'s dispatch and its existing "--phase X requires --root" guard to cover the temporal leaf phases; extend print_report(). Correct the docstring path lie on line 20 and update the Modes block to name the temporal phase.</file>
  </files-to-modify>
  <validation>
    <check>ANTHROPIC_API_KEY="" python scripts/memory_recall_eval.py --phase temporal exits 0 and prints a temporal block. RED before this change (argparse rejects the choice and exits 2), GREEN after.</check>
    <check>grep -n "personal_memory" scripts/memory_recall_eval.py returns nothing. RED before (line 20), GREEN after.</check>
    <check>ANTHROPIC_API_KEY="" python scripts/memory_recall_eval.py --phase all still prints the same hit@1 and hit@3 counts as before the change — the existing phases are untouched.</check>
    <check>python scripts/memory_recall_eval.py --phase capture --scenario-set temporal exits nonzero with "requires --root".</check>
    <check>After a full temporal run, neither ~/.attune/memory nor the repo's .attune/memory contains any scenario topic slug: ls ~/.attune/memory 2>/dev/null | grep -c t1-changed prints 0.</check>
  </validation>
  <risks>
    <risk severity="medium">os.utime on the captured file sets mtime, but PersonalMemory may re-derive summaries or touch the file on a later write. Apply the utime after every capture in the scenario completes, and assert the aged mtime survives into the evaluate process.</risk>
    <risk severity="medium">At DEFAULT_VOLATILITY 0.75 every captured personal memory crosses check-before-acting at roughly 14 days and suspect at roughly 60 days on file age alone. Session ages must be chosen deliberately against those constants, and the report must not present a tier label as evidence the fact changed.</risk>
    <risk severity="low">scripts/ is in pyproject.toml's ruff exclude list, so nothing lints this file. Match the surrounding style by hand.</risk>
  </risks>
  <dependencies>
    <dep>T2</dep>
    <dep>T3</dep>
  </dependencies>
</task>

<task id="T5" name="Slot-occupancy scoring and the recall-is-not-staleness guard">
  <objective>
    Implement the metric that answers the actual question. Primary: per scenario, did the current fact occupy slot 1, and where did the superseded one land. Report the winner's topic, the loser's topic, both raw scores, the margin between them, and both staleness and status annotations. For the tie-break judgement use a within-run relative criterion in the shape of the D3 rule already ruled in docs/specs/memory-recall-eval — no absolute cutoff, because the script's own comment establishes that score is an unbounded raw keyword-overlap count with no universal threshold. Report hit@k over the temporal set too, labelled in the output as DIAGNOSTIC, NOT A PASS CONDITION with the one-line reason. Make the report structurally incapable of the trap: a run in which every scenario recalls its current fact at k=3 while the superseded fact wins slot 1 must come out as a FAILURE, not a pass with a caveat.
  </objective>
  <files-to-modify>
    <file path="scripts/memory_recall_eval.py">evaluate_temporal() returns per-scenario records with slot1_topic, expected_winner, margin, both annotations, and a passed boolean derived from slot occupancy alone. The returned dict carries slot1_current_fact_wins as a count of named cases, must_pass_cases, and a separate diagnostic block holding hit@1 and hit@3. print_report()'s temporal block prints the diagnostic under its own header carrying the non-pass-condition sentence.</file>
  </files-to-modify>
  <validation>
    <check>Construct a synthetic results dict where every scenario has the current fact in the top 3 but the stale topic in slot 1, pass it to the report path, and the overall verdict is FAILED. RED before this change (no such code path), GREEN after — pinned as a test in T7.</check>
    <check>The JSON dump from --phase temporal --json-out contains slot1_current_fact_wins, must_pass_cases, and a diagnostic key, and the diagnostic key holds the hit@k numbers.</check>
    <check>grep -n "DIAGNOSTIC" scripts/memory_recall_eval.py shows the label on the hit@k output path.</check>
    <check>No scenario's pass boolean is computed from any hit@k value: grep the pass computation and confirm it reads only slot-1 topic identity.</check>
  </validation>
  <risks>
    <risk severity="medium">Scoring on the status annotation alone measures when the file was last written, not whether the fact changed — the same class of trap the plan warns about for recall. Slot identity is the pass condition; annotations are reported as context.</risk>
    <risk severity="medium">If the two competing topics tie exactly, slot 1 is decided by the sort's stability and the +0.001 project tiebreak, not by anything about time. Report exact ties as a distinct outcome rather than folding them into pass or fail.</risk>
  </risks>
  <dependencies>
    <dep>T4</dep>
  </dependencies>
</task>

<task id="T6" name="Port the threshold gate and lock the temporal baseline">
  <objective>
    attune-ai has no thresholds file and no check_thresholds equivalent — a search for threshold data files across attune-ai, attune-forms and attune-verify returns none. precision_at_1 gates from attune-rag/docs/specs/release-quality-baseline/thresholds.json via attune-rag/scripts/check_thresholds.py at attune-rag/.github/workflows/benchmark.yml line 158. Port that mechanism rather than pretending one exists here. Write the thresholds file in the same shape, with the metric expressed as an absolute count of named must-pass cases rather than a rate, and add a checker with the house exit-code contract: 0 pass, 1 regression, 2 validation error, a check() returning (failures, validation_errors) so a malformed dump fails loudly instead of passing quietly, one FAIL line per failure on stderr, and a fixture sha256 binding so the gate cannot be met against a swapped scenario set. Populate the thresholds from the T1 matrix, which was committed before the first run.
  </objective>
  <files-to-create>
    <file path="docs/specs/temporal-staleness/thresholds.json">{commit, measured_at, metrics: {slot1_current_fact_wins: {measured, threshold}}, must_pass_cases: [case ids from D1], fixture_path: "scripts/memory_recall_eval.py", fixture_sha256, runs}. Threshold is a count, not a percentage.</file>
    <file path="scripts/check_temporal_thresholds.py">Stdlib-only gate. _load_json, extract_metrics(dump), check(dump, thresholds, verify_fixture_sha256) returning (failures, validation_errors), main() with --dump/--thresholds/--skip-fixture-sha-check. Exit 0 pass, 1 regression, 2 validation error. Apache-2.0 footer in the module docstring, since this is a new file.</file>
  </files-to-create>
  <validation>
    <check>python scripts/check_temporal_thresholds.py --dump &lt;a passing dump&gt; --thresholds docs/specs/temporal-staleness/thresholds.json exits 0.</check>
    <check>Hand-edit the dump so one must-pass case fails; the script exits 1 and prints exactly one FAIL line naming that case id on stderr.</check>
    <check>Feed a dump missing the slot1_current_fact_wins key; the script exits 2, not 0 and not 1.</check>
    <check>Change one character in TEMPORAL_SCENARIOS and re-run against the locked thresholds without regenerating the sha; the script exits 2 with a fixture-mismatch message.</check>
  </validation>
  <risks>
    <risk severity="medium">Binding fixture_sha256 to the whole of scripts/memory_recall_eval.py makes every unrelated edit to that script break the gate. Hash a canonical serialization of TEMPORAL_SCENARIOS instead, and say in the thresholds file exactly what was hashed.</risk>
    <risk severity="medium">Locking thresholds after the first run inverts the discipline. The numbers come from the D1 matrix committed in T1; if the first run disagrees, the honest move is a dated decisions entry, not an edited threshold.</risk>
  </risks>
  <dependencies>
    <dep>T1</dep>
    <dep>T5</dep>
  </dependencies>
</task>

<task id="T7" name="Tests for the phase, the scoring, the presentation and the gate">
  <objective>
    Neither eval script has any test today — a grep across tests/ for memory_recall_eval and eval_personal_memory_recall returns nothing, and scripts/ is excluded from ruff, so this work is being built on uncovered, unlinted code. Add coverage for the new surface following the house pattern for scripts: REPO_ROOT = Path(__file__).resolve().parents[3], SCRIPT_PATH = REPO_ROOT / "scripts" / "memory_recall_eval.py", and a module-scoped fixture loading it via importlib spec_from_file_location, module_from_spec, sys.modules registration and exec_module, exactly as tests/unit/scripts/test_ledger_precision.py does. Pin the properties that matter: fixture drift exits nonzero; the temporal leaf phases refuse to run without --root; a stale-wins-slot-1 result is a FAILURE even when hit@3 is perfect; a high-signal T4 payload survives capture() and still carries its instruction flags at query time; a curated bare imperative correctly does NOT flag. Add a gate test pinning the thresholds file schema and its fixture-sha binding.
  </objective>
  <files-to-create>
    <file path="tests/unit/scripts/test_memory_recall_eval_temporal.py">Loads the script via importlib. Module docstring states which property is pinned and why, in the manner of tests/unit/memory/test_provenance.py. Inherits the autouse hermetic fixture from tests/unit/scripts/conftest.py.</file>
    <file path="tests/unit/gates/test_temporal_thresholds_schema.py">Pins docs/specs/temporal-staleness/thresholds.json keys, that the threshold is an integer count and not a float in [0,1], and that must_pass_cases is non-empty and matches the case ids in TEMPORAL_SCENARIOS.</file>
  </files-to-create>
  <files-to-modify>
    <file path="tests/unit/memory/test_provenance.py">Cases for the status argument on wrap_recalled and for the by-design non-flag on the curated tier, keeping the existing posture that tests assert framing, never neutralisation.</file>
    <file path="tests/unit/test_cli_memory_commands.py">Pin that cmd_memory_recall's human output carries the staleness label, so the CLI surface cannot silently drift back to raw prose.</file>
  </files-to-modify>
  <validation>
    <check>python -m pytest tests/unit/scripts/test_memory_recall_eval_temporal.py tests/unit/gates/test_temporal_thresholds_schema.py -q passes.</check>
    <check>python -m pytest tests/unit/memory/ tests/unit/test_cli_memory_commands.py -q passes.</check>
    <check>The stale-wins-slot-1 test fails if the pass computation in evaluate_temporal is changed to read hit@3 — verify by making that edit locally, watching the test go red, and reverting.</check>
    <check>python -m pytest tests/unit/scripts/test_memory_recall_eval_temporal.py -n 4 passes, confirming parallel safety under the repo's -n auto default.</check>
    <check>No new pytest marker is used: grep -n "pytest.mark" on the new test files shows only markers already registered in pytest.ini.</check>
  </validation>
  <risks>
    <risk severity="medium">The subprocess-forking temporal orchestrator is slow to run inside a unit test. Test the leaf phases and the scoring functions directly, and cover the orchestrator with one guarded end-to-end case rather than one per scenario.</risk>
    <risk severity="low">pytest.ini sets filterwarnings = error. A new test that triggers a warning outside the four ignored categories fails the suite.</risk>
  </risks>
  <dependencies>
    <dep>T4</dep>
    <dep>T5</dep>
    <dep>T6</dep>
  </dependencies>
</task>

<task id="T8" name="CI wiring, first run, and the dated verdict">
  <objective>
    Wire the gate the way precision is wired in the sibling package: a job that runs --phase temporal --json-out and feeds the dump to scripts/check_temporal_thresholds.py, with a timeout, pinned action SHAs, a concurrency group and ANTHROPIC_API_KEY set to the empty string — the constraints tests/unit/ci/test_workflow_yaml.py and tests/unit/ci/test_ci_spend_guard.py enforce. Then run the benchmark once and write ONE dated decisions.md entry in house style: the per-case matrix outcome against the T1 pre-commit, what the run establishes and explicitly what it does NOT, the conflict-presentation decision as implemented, and the T4 result including the by-design non-flags. Add the CHANGELOG [Unreleased] entry the changelog gate requires, and update the Health checks section of docs/how-to/which-memory-is-which.md, which today names only the release recall gate.
  </objective>
  <files-to-create>
    <file path=".github/workflows/memory-temporal.yml">Runs the temporal phase and the checker on pull_request and push to main. Timeout, pinned action SHAs, concurrency group, permissions contents: read, ANTHROPIC_API_KEY: "" — the shape tests/unit/ci/test_workflow_yaml.py checks.</file>
  </files-to-create>
  <files-to-modify>
    <file path="docs/specs/temporal-staleness/decisions.md">Append one dated entry with the first run's per-case outcome against D1, stating in its own words what the measurement does and does not establish, and refusing to convert the case counts into a rate.</file>
    <file path="CHANGELOG.md">An [Unreleased] entry; changelog-gate.yml runs on every PR with no path filter.</file>
    <file path="docs/how-to/which-memory-is-which.md">Extend the Health checks section so it names the temporal gate alongside scripts/release_recall_gate.py.</file>
    <file path="scripts/release_recall_gate.py">Consider adding the temporal round-trip to the release path, since this script is already the memory family's release gate at .github/workflows/publish-pypi.yml line 47. If it is not added, say why in the decisions entry rather than leaving the omission silent.</file>
  </files-to-modify>
  <validation>
    <check>python -m pytest tests/unit/ci/test_workflow_yaml.py tests/unit/ci/test_ci_spend_guard.py -q passes with the new workflow present.</check>
    <check>grep -n "ANTHROPIC_API_KEY" .github/workflows/memory-temporal.yml shows the empty-string form, not an unset variable and not a secret reference.</check>
    <check>The workflow's checker step exits 0 on the committed thresholds and the first run's dump, and the run's job log shows the DIAGNOSTIC label on the hit@k lines.</check>
    <check>grep -nE "[0-9]+%" docs/specs/temporal-staleness/decisions.md shows no pass condition stated as a rate.</check>
    <check>grep -n "temporal" docs/how-to/which-memory-is-which.md returns a line inside the Health checks section.</check>
  </validation>
  <risks>
    <risk severity="high">This arms a CI check that can block merges on a handful of hand-authored cases. The memory-recall-eval entry dated 2026-08-28 ruled that a behaviour gate here is PENDING and fixed the precondition order: define the acceptance criterion, expand the negative set, then wire CI. A human must confirm the per-case matrix satisfies that order before this job becomes required rather than advisory.</risk>
    <risk severity="medium">Adding the temporal round-trip to release_recall_gate.py puts it on the publish path, where a false failure blocks a release. If added, it must run against a tmp root and an isolated fake HOME exactly as the existing gate does.</risk>
    <risk severity="medium">The first run may disagree with the pre-committed matrix. The rule is to record the disagreement in the dated entry, not to edit D1 — "Numbers revisitable only with stated reason before the run, never after".</risk>
  </risks>
  <dependencies>
    <dep>T6</dep>
    <dep>T7</dep>
  </dependencies>
</task>

---

## Reference

**Files being modified**

- `scripts/memory_recall_eval.py` — 416 lines. `CorpusEntry`, `CORPUS` (18 entries), `Query`, `QUERIES` (18 positive + 5 negative), `capture_corpus(global_root)`, `evaluate(global_root)`, `run_benchmark()`, `run_persistence_benchmark()`, `print_report(results)`, `main()`. `--phase all|persistence|capture|evaluate`, `--root`, `--json-out`. No licence header — match the file, do not add one mid-file. Module docstring line 20 names `~/.attune/personal_memory`, a path that exists nowhere else in `src/` or `scripts/`; the real default is `~/.attune/memory`.
- `src/attune/memory/personal.py` — `_GLOBAL_ROOT = Path.home() / ".attune" / "memory"` at line 32. `query()` at line 242 calls `_annotate_staleness(results)` at line 310 then `_stamp_provenance(results)` at line 311. `_stamp_provenance` at line 328 builds provenance from `hit["excerpt"] or hit["summary"]` with `tier="curated"`. `_annotate_staleness` at line 353 stamps `unverified_days`, `staleness`, `status`. `capture()` writes `root/TOPIC/KIND.md` via `atomic_write_text`, which replaces destructively with no versioning.
- `src/attune/memory/provenance.py` — 280 lines. `scan_instructions(text, *, tier=None)` at line 97, `provenance_fields(...)` at line 127, `wrap_recalled(text, *, tier, source, author_class, instruction_flags=None)` at line 167, `render_recall_for_context(...)` at line 213. `UNTRUSTED_TIERS = frozenset({"raw", "machine", "machine-extracted"})` at line 94; `_DIRECTIVE_PATTERNS` at line 82 fire only on those tiers, so a bare imperative in a curated memory is deliberately not flagged.
- `src/attune/cli_commands/memory_commands.py` — `cmd_memory_recall` prints `hit['score']`, `hit['path']`, `hit['summary']` and `hit['excerpt']` raw at lines ~186-193, with no envelope and no staleness label, after `contextlib.redirect_stdout` suppresses structlog noise.
- `src/attune/mcp/memory_handlers.py` — `_handle_personal_memory_recall` at line 405 renders `render_recall_for_context(hits)` into `context` and strips `summary` and `excerpt` from every structured result; fails closed on ImportError.
- `docs/how-to/which-memory-is-which.md` — Health checks section at line 64+, currently naming `attune memory topics` and `scripts/release_recall_gate.py`.

**Model being reused, not rebuilt**

- `src/attune/memory/curated_audit.py` — 815 lines. `VOLATILITY_BY_TYPE` (project 1.00, reference 0.60, lesson 0.40, feedback 0.15, user 0.10), `DEFAULT_VOLATILITY = 0.75`, `load_memory(path)` (never raises), `resolve_age_basis(mem, latest_verdict)` returning a date and one of verified / verified-unbound / invalidated / tombstoned / mtime, `unverified_age_days(mem, today=None, latest_verdict=None)` with an injectable `today` so tests need no clock control, `epistemic_tier()` against `TIER_SETTLED_MAX = 10.0` and `TIER_CHECK_MAX = 45.0`, `format_status_annotation()`, `format_age_annotation()`. Already covered by `tests/unit/memory/test_curated_audit.py`.
- `src/attune/memory/verdict_log.py` — `latest_verdicts(root)` mapping stem to `VerdictRecord`, consumed by both `PersonalMemory._latest_verdict_for` and `curated_audit.resolve_age_basis`.

**Prior art being mirrored**

- Multi-process phase architecture: `scripts/memory_recall_eval.py::run_persistence_benchmark()` — one `tempfile.mkdtemp()` root, `subprocess.run([sys.executable, script, "--phase", "capture", "--root", ...], check=True)`, then a second subprocess with `--phase evaluate --json-out`, results read from a file because structlog corrupts stdout, everything torn down in a `finally`.
- Relative, self-calibrating criterion: `scripts/eval_personal_memory_recall.py`, ruled as OQ3 option (a) / D3 in `docs/specs/memory-recall-eval/design.md` — threshold derived within the run from the minimum correct-positive top-1 score, with "criterion inapplicable" reported instead of a fake number in degenerate cases.
- Threshold gate to port: `attune-rag/scripts/check_thresholds.py` (338 lines; `MetricFailure`, `extract_metrics`, `check() -> (failures, validation_errors)`, exit 0/1/2, `--skip-metric`, `format_failure_comment()`), its locked baseline `attune-rag/docs/specs/release-quality-baseline/thresholds.json`, its consumer `attune-rag/.github/workflows/benchmark.yml` line 158, and its tests `attune-rag/tests/unit/test_check_thresholds.py`. Smallest credible variant: `attune-verify/scripts/mutation_gate.py`.
- Fixture-drift discipline: `scripts/phase0/lessons_rag_benchmark.py` cross-checks every expected slug against the live corpus and returns 1 before reporting any number.
- Release-path gate in this family: `scripts/release_recall_gate.py` (160 lines; isolated fake `HOME`, env built from scratch with `ANTHROPIC_API_KEY: ""`, wheel install, capture-to-recall round-trip, duplicate-path assertion), wired at `.github/workflows/publish-pypi.yml` line 47.
- Pre-committed matrix template: `docs/specs/archive/lessons-corpus-rag/decisions.md` D1 — benchmark shape, a three-row Result/Decision table, an explicit note on what is motivational versus a gate, high-severity cases tagged in the fixture before the first run, and "the commit timestamp is the arbiter". Sibling clause in `docs/specs/archive/ams-int8-quantization/decisions.md`: "Numbers revisitable only with stated reason before the run, never after."
- Test-a-script pattern: `tests/unit/scripts/test_ledger_precision.py` (importlib loading via `spec_from_file_location`) and `tests/unit/scripts/conftest.py` (autouse hermetic ledger fixture).
- Test posture to copy: `tests/unit/memory/test_provenance.py` — "assert framing and labelling, never that a payload is neutralised", plus `test_directive_flagged_only_for_untrusted_tier` and `test_curated_dev_imperatives_are_not_flagged`, which pin the curated non-flag as intentional.
- mtime forgery precedent: `os.utime` in roughly 20 test modules, e.g. `tests/unit/ops/test_memory_attention.py` line 35 and `tests/unit/ops/test_completion_candidates.py` line 137.
- Human-review half of the protocol, already shipped: `scripts/review_curated_memory.py` (keep / wrong / sharper, queue capped at 3) and `scripts/audit_curated_memory.py` ("Advisory only. This script never writes to a corpus and always exits 0 — it is not a gate.").
- The only shipped abstention mechanism: `plugin/hooks/lesson_recall.py` filters on `h.score >= floor` with floor 8.0 from `ATTUNE_LESSON_RECALL_FLOOR`. `PersonalMemory` has no floor at all. If conflict presentation ever needs a suppression lever, this is the precedent and its measured failure shape.

**Governing text**

- `attune-ai-dev/discipline/COLLABORATION_DISCIPLINE.md` §5, lines ~684-710 — the two-layer protocol, ratified 2026-07-02 as D6, with the receipt at line 157 and lines 1133-1134. Draft source: `docs/process/COLLABORATION_DISCIPLINE_revision_2026-07-02_proposal.md` §C3, receipt [R-B].
- `docs/specs/memory-status-integrity/requirements.md` — R2 ("a reader must see how long it has been since a claim was confirmed") and D1 (label, never suppress by age). The closest existing spec to this work.
- `docs/specs/memory-recall-eval/decisions.md` — 584 lines, 12 dated entries. The 2026-08-28 chair-directed re-run sets the precondition order for arming a behaviour gate and forbids reading small counts as rates.
- `AGENTS.md` principle 6 (CI spends attention, never money), 15 (degrade gracefully around the memory layer), 16 (claims carry their basis). Session protocol: run `python scripts/collaboration_preflight.py` before non-trivial work.

**Constraints that will bite**

- `pytest.ini`: `--strict-markers`, `-n auto`, `filterwarnings = error`, `pythonpath=src`. No new marker without registering it first; tests must be parallel-safe and must not write to `$HOME`.
- `pyproject.toml`: `[tool.ruff]` exclude includes `scripts/`, so CI catches no style problem in the eval script. `B904` is enforced in `src/` — `raise ... from e`.
- Licence footer (`Copyright <year> Smart AI Memory, LLC` / Apache-2.0) goes in the module docstring of NEW files only; `scripts/memory_recall_eval.py` has none and should not gain one mid-change.
- `.github/workflows/changelog-gate.yml` runs on every PR with no path filter.