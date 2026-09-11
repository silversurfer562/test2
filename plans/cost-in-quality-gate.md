# Plan: Cost joined to quality

**Spec**: [specs/cost-in-quality-gate/](../../specs/cost-in-quality-gate/)
**Created**: 2026-09-11

---

## Summary

attune-rag measures selectivity and does not measure economics. `src/attune_rag/benchmark.py::_run_benchmark` returns `retriever`, `corpus`, `total_queries`, `precision_at_1`, `recall_at_k`, `k`, `mean_latency_ms`, `max_latency_ms`, `by_difficulty`, `per_query` — ten keys, none of them a dollar figure. The locked gate at `docs/specs/release-quality-baseline/thresholds.json` carries three rows (`precision_at_1`, `recall_at_3`, `mean_faithfulness`), all quality. The product thesis is "selectivity × economics"; the README's hero table states the first half in four figures and the second half nowhere. Shipping this plan makes "the lightweight tier is the cheap one" a measured claim with a dated price stamp behind it instead of an architectural assertion.

The research pass contradicted the brief on eight points, and the code wins each one. **(1) The price table is not in `cost_tracker.py`.** That file imports `MODEL_REGISTRY`, `ADDITIONAL_MODELS` and `TIER_PRICING` from `attune.models.registry` at lines 27-28 and flattens them; only a 3-key `legacy_models` dict is local. The real table is `attune-ai/src/attune/models/registry.py`, with ~13 module-scope import sites and a fourth hand-copied rate pair in `ops/session_summarizer.py:42-48`. **(2) `model_tiers.py`'s pattern cannot be mirrored precisely** — the re-export there is lazy because `attune.config` must not pay for `attune_rag/__init__` (~350 modules), and `from attune.models.registry import TIER_PRICING` sits at module scope in `agents/release/base_agent.py` and `routing/model_router.py`. So this plan moves the *numbers* (stdlib-only, no `ModelInfo`, no config-shaped converters) and leaves the dataclass and its converters where their consumers are. **(3) The benchmark's default path spends $0.00.** `_run_benchmark`'s own docstring says "Pure: no LLM calls, no disk writes"; all three `--retriever` choices run locally. A `cost_per_query_usd: 0.0` on a retrieval-only run asserts "free" where the truth is "not measured", so every USD field is `None` unless a token-spending pass actually ran. **(4) attune-rag has no token accounting at all** — `LLMProvider.generate` returns `str`, `CitedResponse` is `(text, claim_citations)`, `FaithfulnessResult` has no token fields, and nothing reads `response.usage`. Cost is a plumbing change before it is a reporting change, and it is T4 of 8 for that reason.

The gate contradictions are sharper. **(5)** `check_thresholds.check()` fails on `measured[metric] < threshold` for every metric and `measure_baseline_variance.compute_stats` emits `mean − σ·stdev`, so a cost row in that file would fail a $0.0001 run and pass a $1.00 one; the repo already solved the inverted case in `scripts/measure_perf_baseline.py` (`mean + σ·stdev`, "inverted sign per Decision 1"), and this plan gives the quality gate the same per-metric direction concept. **(6)** `thresholds.json` is machine-generated — `write_thresholds_json` rebuilds the whole payload from `stats_by_metric`, so a hand-added cost row is destroyed by the exact re-measure command the gate's own failure comment tells maintainers to run; the row must be produced by the measuring script, which scrapes **stdout**, not the JSON dump, so the metric must also be printed in a regex-matchable line. **(7)** A newly-required metric breaks CI two ways: `check_thresholds` treats a threshold with no measured counterpart as exit 2, and `scripts/smoke_check_gate.sh` runs with `if: always()` on every PR with synthetic dumps that have no cost field. **(8)** There is no green-run comment to put a delta in — `format_failure_comment` raises `ValueError` on an empty failure list ("callers should skip commenting on a green run") and benchmark.yml's comment step is gated on `rc == '1'`. The vehicle the brief wants already exists in `perf.yml`'s `delta-check` job plus `scripts/format_perf_delta.py`, so this plan builds `scripts/format_cost_delta.py` on that pattern and adds an advisory job to `benchmark.yml` — the brief's file, the other workflow's mechanism.

Two limitations stated at full strength. First, on the default state of this repo `ANTHROPIC_API_KEY` is absent from Secrets (benchmark.yml's own header says so), so every PR cost comment will read "not measured" until a key is configured; that is the honest output, and it is the reason the USD fields are nullable rather than zero-valued. Second, locking a cost threshold costs real money — `measure_baseline_variance` needs ≥10 runs and `_score_faithfulness` spends 2 LLM calls per query per run — so the cost row lands via one deliberate maintainer-run lock, and `--max-cost` is advisory until it does.

---

## Tasks

<task id="T1" name="Settle the move boundary and write the spec">
  <objective>Decide, in writing and before any code, how far the price table moves. Enumerate the real table (attune-ai/src/attune/models/registry.py: ModelInfo, MODEL_REGISTRY, ADDITIONAL_MODELS, TIER_PRICING) and its module-scope import sites, then choose between (a) moving the whole registry, (b) extracting a stdlib-only rate table into attune-rag with attune-ai keeping ModelInfo and its config-shaped converters, or (c) giving attune-rag its own benchmark-scoped table. Option (b) is the recommendation: it is the only one that preserves model_tiers.py's actual invariant (stdlib-only, no I/O, importable on a light path) without dragging attune-ai's config contract across the boundary, and without putting attune_rag's ~350-module package init behind `from attune.models.registry import TIER_PRICING`. Record the decision with the measured import cost of the rejected option, the three dated-price comments to be replaced by a machine-readable field (registry.py:524, session_summarizer.py:42-48, cost_tracker.py's BASELINE_MODEL note), and the key trap: cost per CALL hides retries and re-retrieval, so the denominator for the headline figure is successful queries, not calls.</objective>
  <files-to-create>
    <file path="docs/specs/cost-in-quality-gate/README.md">One-page statement of the gap and the eight code-verified contradictions with the brief, each with the file and line that settles it.</file>
    <file path="docs/specs/cost-in-quality-gate/requirements.md">What must be true when this ships: a dated price stamp in every benchmark artifact, a cost-per-successful-query figure, a gate that fails in the right direction, and a README claim backed by a committed measurement.</file>
    <file path="docs/specs/cost-in-quality-gate/design.md">The chosen move boundary, the nullable-USD-field contract, the per-metric threshold direction, and the advisory-comment mechanism copied from perf.yml.</file>
    <file path="docs/specs/cost-in-quality-gate/decisions.md">Numbered decisions: D1 move boundary (a/b/c with the measured import cost of the rejected eager option); D2 USD fields are None when unmeasured, never 0.0; D3 cost threshold direction lives per-metric in thresholds.json; D4 the cost delta gets its own marker and its own advisory job rather than extending the regression-only gate comment; D5 registry.py's rate literals are validated against the canonical table for one release and the guard is deleted when they become accessors.</file>
    <file path="docs/specs/cost-in-quality-gate/risks.md">The key trap (cost per call vs per successful query), the zero-vs-null trap, the machine-generated-thresholds trap, the CI-breaks-on-every-PR trap, and the drift-guard concession in D5.</file>
    <file path="docs/specs/cost-in-quality-gate/tasks.md">T1-T8 with status, mirroring this plan.</file>
  </files-to-create>
  <validation>
    <check>`ls docs/specs/cost-in-quality-gate/` lists README.md, requirements.md, design.md, decisions.md, risks.md, tasks.md. RED before (the directory does not exist), GREEN after.</check>
    <check>`grep -c 'successful' docs/specs/cost-in-quality-gate/risks.md` returns at least 1, and the entry states why a per-call denominator hides retries and re-retrieval.</check>
    <check>decisions.md D1 names the option taken and quotes a number from `python -X importtime -c "import attune.models.registry"` run in ../attune-ai for the rejected eager-import option. Another engineer can re-run that command and compare.</check>
    <check>decisions.md cites registry.py:524, session_summarizer.py:42-48 and cost_tracker.py's legacy_models block by path and line, and each cited line still says what the decision claims it says.</check>
  </validation>
  <risks>
    <risk severity="medium">Choosing option (a) — moving the whole registry — turns a one-week task into a cross-repo refactor of ~13 import paths and three symbol families. If the spec picks (a), the remaining tasks in this plan are mis-sized.</risk>
    <risk severity="low">A spec dir that restates the brief instead of the code re-imports the eight contradictions into the implementation. Each decision must cite a path and a line.</risk>
  </risks>
</task>

<task id="T2" name="Create the canonical price table in attune-rag">
  <objective>Add `src/attune_rag/pricing.py` as the single copy of the token-rate numbers, per T1's decision. Mirror `src/attune_rag/model_tiers.py` where the pattern applies: stdlib-only imports, no licence header (attune-rag convention — `grep -rl Copyright src/` returns nothing), and a narrative docstring that states the ownership claim, the 2026-04-30 core-dependency fact, the import-weight constraint, and the price-history rule lifted from cost_tracker.py's legacy_models block (legacy model ids keep their own rates; never remap `claude-opus-4-20250514` to `claude-opus-4-8`, which is $5/$25 and would mis-price history). Export `PRICE_TABLE` (model id to `{"input", "output"}` per million tokens), `TIER_PRICE_TABLE` (cheap/capable/premium aliases), `PRICE_TABLE_DATED` as an ISO date string field — this is the whole point, the three existing dated prices in the family are comments and cannot be surfaced in an artifact — and `price_for(model_id)` which raises ValueError naming the unknown id and listing the known set, rather than falling back to the capable tier the way `CostTracker._calculate_cost` does. Do not export a mutable module-level dict without a fresh-copy accessor; the test suite pins mutation safety.</objective>
  <files-to-create>
    <file path="src/attune_rag/pricing.py">The canonical rate table, its dated stamp as a field, and price_for(). Stdlib-only so consumers can import it on light paths.</file>
    <file path="tests/unit/test_pricing.py">Pins the table contents, the dated stamp's format, the unknown-id ValueError, and mutation safety — mirroring tests/unit/test_model_tiers.py's class groupings and literal-pin test.</file>
  </files-to-create>
  <files-to-modify>
    <file path="CHANGELOG.md">Add an `### Added` entry under `## [Unreleased]` in the existing bold-lead-sentence style, stating that attune_rag.pricing is the single copy of the rate table and what the surface impact is.</file>
  </files-to-modify>
  <validation>
    <check>`python -c "from attune_rag.pricing import PRICE_TABLE, PRICE_TABLE_DATED, price_for; print(PRICE_TABLE_DATED, price_for('claude-haiku-4-5'))"` prints an ISO date and a rate dict. RED before (ModuleNotFoundError), GREEN after.</check>
    <check>`grep -nE '^\s*(import|from) ' src/attune_rag/pricing.py` shows only stdlib modules — no structlog, anthropic, yaml, jinja2 or rich.</check>
    <check>`grep -c Copyright src/attune_rag/pricing.py` returns 0 (attune-rag files carry no licence header).</check>
    <check>`python -c "from attune_rag.pricing import price_for; price_for('no-such-model')"` exits non-zero and the ValueError message contains the offending id and the sorted known set.</check>
    <check>`python -c "from attune_rag.pricing import price_for; a=price_for('claude-haiku-4-5'); a['input']=999; assert price_for('claude-haiku-4-5')['input'] != 999"` exits 0.</check>
    <check>`uv run pytest tests/unit/test_pricing.py -q` passes.</check>
  </validation>
  <risks>
    <risk severity="medium">Copying the rates out of registry.py by hand introduces a transcription error that silently mis-prices every downstream figure. The T3 equality check is the guard; it must run before any number reaches the README.</risk>
    <risk severity="low">PRICE_TABLE_DATED describes when the rates were last verified against the provider's published prices, not when the file was edited. If it is set from a git timestamp it becomes meaningless.</risk>
  </risks>
  <dependencies>
    <dep>T1</dep>
  </dependencies>
</task>

<task id="T3" name="Re-export from attune-ai and rewire its rate consumers">
  <objective>Add the attune-ai side of the move, copying `src/attune/model_tiers.py`'s lazy shape exactly: thin wrappers with function-local imports carrying `# noqa: PLC0415`, PEP 562 `__getattr__` over a `_LAZY_NAMES` frozenset, TYPE_CHECKING-only imports for static types, `__dir__`, and a docstring explaining why lazy is not optional here (importing `attune_rag.pricing` runs `attune_rag/__init__`, which eagerly loads pipeline, corpus and providers). Rewire `cost_tracker._build_model_pricing()` to source rates from the re-export with a function-local import, keeping the local `legacy_models` block and its do-not-remap comment verbatim — those three keys are historical telemetry lookups, not live rates, and they stay in attune-ai. Decide explicitly and record in decisions.md whether `MODEL_PRICING` stays eager at cost_tracker module scope (it is imported by workflows/cost_mixin.py and workflows/services/cost_service.py, which are already heavy paths) or becomes lazily built; the recommendation is eager, because cost_tracker already imports attune.models and does file I/O. Reconcile the hand-copied rate pair in `ops/session_summarizer.py:42-48` so it derives from the canonical table instead of two literal floats under a dated comment. Per D5, add a test asserting registry.py's rate literals equal the canonical table; this is a drift guard, which the family retired for model_tiers, and it is accepted for one release only because the alternative is an eager attune_rag import behind `from attune.models.registry import TIER_PRICING` at module scope in agents/release/base_agent.py and routing/model_router.py. Say so in the PR and name the follow-up that deletes it.</objective>
  <files-to-create>
    <file path="../attune-ai/src/attune/pricing.py">Lazy PEP 562 re-export of attune_rag.pricing, with the Apache header attune-ai files carry.</file>
    <file path="../attune-ai/tests/unit/test_pricing.py">Twin test exercising the same contract through the re-export path, per the model_tiers twin-test precedent, plus the import-laziness assertion and the registry-literal equality guard.</file>
  </files-to-create>
  <files-to-modify>
    <file path="../attune-ai/src/attune/cost_tracker.py">_build_model_pricing() sources rates from attune.pricing via a function-local import; legacy_models and its do-not-remap comment are untouched.</file>
    <file path="../attune-ai/src/attune/ops/session_summarizer.py">Replace the two hand-copied floats and their dated comment with a lookup against the canonical table.</file>
    <file path="../attune-ai/src/attune/models/registry.py">Replace the dated-price comment at the TIER_PRICING tail with a reference to PRICE_TABLE_DATED; rate literals stay for this release under the D5 guard.</file>
    <file path="../attune-ai/pyproject.toml">Bump the attune-rag floor on the existing core-dependency line with an inline rationale in the established style, naming the first release that ships attune_rag.pricing.</file>
    <file path="../attune-ai/CHANGELOG.md">`### Changed` entry under `## [Unreleased]` stating that rate numbers now come from attune-rag and that MODEL_PRICING's contents are unchanged.</file>
  </files-to-modify>
  <validation>
    <check>From ../attune-ai: `python -X importtime -c "import attune.pricing" 2>&1 | grep -c "attune_rag"` returns 0 — the re-export does not pay for attune_rag's package init at import time.</check>
    <check>From ../attune-ai: `python -c "import sys, attune.pricing; assert 'attune_rag.pricing' not in sys.modules; print(attune.pricing.price_for('claude-haiku-4-5'))"` exits 0 and prints a rate dict.</check>
    <check>From ../attune-ai: `python -c "from attune.cost_tracker import MODEL_PRICING as P; from attune_rag.pricing import PRICE_TABLE as T; bad=[m for m in T if P.get(m)!=T[m]]; assert not bad, bad"` exits 0. RED before (the module does not exist), GREEN after.</check>
    <check>From ../attune-ai: `python -c "from attune.cost_tracker import MODEL_PRICING as P; assert P['claude-opus-4-20250514']=={'input':15.00,'output':75.00}"` exits 0 — price history is not remapped.</check>
    <check>From ../attune-ai: `grep -n 'as of 2026-05' src/attune/ops/session_summarizer.py` returns nothing, and the module's rates resolve through the canonical table.</check>
    <check>From ../attune-ai: `uv run pytest tests/unit -k "pricing or cost_tracker or model_tiers" -q` passes.</check>
  </validation>
  <risks>
    <risk severity="high">MODEL_PRICING backs every cost figure attune-ai reports. A wrong or missing key does not raise — CostTracker._calculate_cost falls back to the capable tier price — so a rewiring bug silently under-reports spend across telemetry, workflows and the release agents. A human must confirm the equality check above and the legacy-key assertion before this merges.</risk>
    <risk severity="medium">If the re-export is written eagerly, or if registry.py imports attune_rag at module scope, `from attune.models.registry import TIER_PRICING` in agents/release/base_agent.py starts pulling ~350 modules. The importtime check is the guard and must stay in the test suite, not just in this plan.</risk>
    <risk severity="medium">D5's equality guard is a drift test, which is the pattern the family deliberately retired for model_tiers. Shipping it without the follow-up that deletes it leaves two copies of the numbers with a test in between.</risk>
  </risks>
  <dependencies>
    <dep>T2</dep>
  </dependencies>
</task>

<task id="T4" name="Thread token usage through attune-rag's LLM paths">
  <objective>The prerequisite the brief omits: attune-rag captures no token counts anywhere. `LLMProvider.generate` returns a bare str, `CitedResponse` is `(text, claim_citations)`, `FaithfulnessResult` has score/claims/reasoning/thinking_used and no token fields, and the only grep hits for input_tokens are a docstring aside in providers/claude.py:224-225. Add a frozen `TokenUsage` dataclass to providers/base.py (input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens, model), add an optional `usage: TokenUsage | None = None` field to `CitedResponse`, and add `generate_with_usage(...) -> tuple[str, TokenUsage | None]` to the LLMProvider Protocol with a body that delegates to `generate()` and returns `(text, None)` so third-party providers stay conformant. Implement it in ClaudeProvider from `response.usage`, including the cache fields claude.py already documents. Carry usage onto `RagResult` (frozen, already has defaulted fields) and onto `FaithfulnessResult` plus its `to_dict()`. Follow attune-forms/benchmarks/provider.py: when the SDK returns no usage, record None — never default to zero, which reports a real run as free. Handle the subscription route explicitly: `FaithfulnessJudge.score(auth_mode='sub')` goes through claude-agent-sdk and its per-token dollar cost is not comparable to API billing, so tag those records `billing_mode="subscription"` and leave them out of the USD aggregates rather than pricing them. `attune_rag.providers.__all__` is `{LLMProvider, get_provider, list_available}` and does not need to change, but the Protocol contract and the provider tests do.</objective>
  <files-to-create>
    <file path="tests/unit/test_token_usage.py">Pins TokenUsage's shape, the None-not-zero rule when the SDK omits usage, the cache-token fields, and the subscription tagging.</file>
  </files-to-modify>
  <files-to-modify>
    <file path="src/attune_rag/providers/base.py">Add TokenUsage; add the usage field to CitedResponse; add generate_with_usage to the LLMProvider Protocol with a delegating default body.</file>
    <file path="src/attune_rag/providers/claude.py">Populate TokenUsage from response.usage, including cache_read_input_tokens and cache_creation_input_tokens; return None when usage is absent.</file>
    <file path="src/attune_rag/pipeline.py">Carry usage on RagResult through run_and_generate, on both the native-citations and prompt-assembly paths.</file>
    <file path="src/attune_rag/eval/faithfulness.py">Add usage and billing_mode to FaithfulnessResult and its to_dict(); populate from the judge call on the API route, tag the subscription route.</file>
    <file path="tests/unit/test_providers_base.py">Extend for the new Protocol member and the CitedResponse field default.</file>
    <file path="tests/unit/test_contracts.py">Update the frozen contract assertions for the new Protocol member.</file>
    <file path="tests/unit/test_eval_faithfulness.py">Pin the new FaithfulnessResult fields and the to_dict() payload.</file>
    <file path="docs/specs/api-v0.2.0-cut/design.md">Record the provider-surface addition in the module table this spec freezes.</file>
  </files-to-modify>
  <validation>
    <check>`python -c "from attune_rag.providers.base import TokenUsage; print(TokenUsage)"` exits 0. RED before (ImportError), GREEN after.</check>
    <check>`python -c "from attune_rag.providers.base import CitedResponse; r=CitedResponse(text='x', claim_citations=()); assert r.usage is None"` exits 0 — the field defaults to None, so existing constructors are unaffected.</check>
    <check>A ClaudeProvider unit test feeds a stub response with no `usage` attribute and asserts the returned TokenUsage is None, not a zero-filled instance. `uv run pytest tests/unit/providers -q` passes.</check>
    <check>`uv run pytest tests/unit/test_api_surface.py tests/unit/test_contracts.py -q` passes — `attune_rag.providers.__all__` is unchanged.</check>
    <check>`python -c "from attune_rag.eval.faithfulness import FaithfulnessResult; import inspect; assert 'usage' in inspect.signature(FaithfulnessResult).parameters"` exits 0.</check>
  </validation>
  <risks>
    <risk severity="high">This changes a public Protocol that third-party providers implement. A Protocol member without a delegating default body silently breaks every out-of-tree provider at runtime_checkable check time, and the failure surfaces as a retrieval error, not an import error. A human must review the Protocol diff and confirm the default body path is exercised by a test that does not implement the new member.</risk>
    <risk severity="medium">Defaulting absent usage to zero anywhere in this chain makes a real, billed run report as free — the exact failure mode this whole plan exists to prevent. attune-forms/benchmarks/provider.py raises rather than defaulting; the weaker None here must be enforced by the test above.</risk>
    <risk severity="medium">The subscription route's cost is not comparable to API billing. Pricing it with the API table produces a confident wrong number; the billing_mode tag must be checked before any USD aggregate is computed.</risk>
  </risks>
  <dependencies>
    <dep>T1</dep>
  </dependencies>
</task>

<task id="T5" name="Add cost aggregates to the benchmark report, print them, and dump them">
  <objective>Add a `cost` block to the benchmark report dict, following the `_aggregate_by_difficulty` precedent — its docstring is the argument: "Promoted into the report dict (not just the printed summary) so the JSON artifact carries per-difficulty signal". The block carries `cost_per_query_usd`, `cost_per_successful_query_usd`, `total_cost_usd`, `cost_measured_queries`, `billing_mode`, and `price_table_dated` as a field. `_run_benchmark` populates the block with every USD field set to None and `price_table_dated` populated, so the key is always present and its nullness means "not measured" rather than "free" — the three retriever choices all run locally and spend nothing, so a 0.0 here would be a false claim. A new `_aggregate_cost(report, faithfulness_report)` computes the real numbers in `main()` when `--with-faithfulness` ran, because the spend happens in `_score_faithfulness` (2 LLM calls per query: run_and_generate plus judge.score) while the success denominator lives in `_run_benchmark`. The denominator for `cost_per_successful_query_usd` is the queries where top-1 is in expected_in_top_3 — the same `precision_hits` counter `_run_benchmark` already maintains — and the numerator is total spend across all calls including retries and re-retrieval. Guard the zero-denominator case (no top-1 hits) by returning None, not by dividing. Print the figures in `_print_summary` and `_print_faithfulness` in a format measure_baseline_variance's regexes can scrape, and extend both the retrieval-only and the faithfulness `--json` payloads.</objective>
  <files-to-modify>
    <file path="src/attune_rag/benchmark.py">Add _aggregate_cost, the always-present cost block on the report dict, the printed lines, and the cost entries in both --json payload branches.</file>
    <file path="tests/unit/test_benchmark.py">Cover: retrieval-only leaves every USD field None with price_table_dated set; zero successful queries yields None rather than ZeroDivisionError; retries are counted in the numerator; subscription-tagged records are excluded from the USD aggregate.</file>
  </files-to-modify>
  <validation>
    <check>`python -m attune_rag.benchmark --json /tmp/rag-cost.json` then `python -c "import json; c=json.load(open('/tmp/rag-cost.json'))['retrieval']['cost']; assert c['cost_per_query_usd'] is None and c['cost_per_successful_query_usd'] is None and c['price_table_dated']"` exits 0. RED before (KeyError: 'cost'), GREEN after.</check>
    <check>`python -m attune_rag.benchmark 2>&1 | grep -E 'Cost/successful query:'` prints a line, and on a retrieval-only run that line says not measured rather than $0.00.</check>
    <check>A unit test constructs a faithfulness report with 4 queries, 0 top-1 hits and non-zero spend, and asserts `cost_per_successful_query_usd is None` and `cost_per_query_usd` is the real per-query figure.</check>
    <check>A unit test constructs a run where one query took two generate calls and asserts total_cost_usd counts both — cost per call would report the cheaper figure.</check>
    <check>`uv run pytest tests/unit/test_benchmark.py tests/unit/test_benchmark_negatives.py tests/unit/test_benchmark_thinking.py -q` passes.</check>
  </validation>
  <risks>
    <risk severity="medium">Emitting 0.0 instead of None on the retrieval-only path publishes "free" as a measured claim on every default CI run. This is the single most consequential line in the task.</risk>
    <risk severity="medium">Computing the aggregate inside _run_benchmark rather than in main() would silently make the successful-query denominator the retrieval run's hit count while the numerator is empty, producing 0.0 by a different route.</risk>
    <risk severity="low">The printed line format is a contract with measure_baseline_variance's regexes. Changing it later without updating _PERCENT_PATTERNS/_FLOAT_PATTERNS makes the locking script blind, exactly as its own in-file comment warns.</risk>
  </risks>
  <dependencies>
    <dep>T2</dep>
    <dep>T4</dep>
  </dependencies>
</task>

<task id="T6" name="Give the threshold machinery a lower-is-better direction">
  <objective>A cost row cannot go into docs/specs/release-quality-baseline/thresholds.json as it stands. `check_thresholds.check()` fails on `measured[metric_name] < threshold_val` for every metric, and `measure_baseline_variance.compute_stats` emits `mean − sigma*stdev`, so a $0.0001 run would fail a $0.01 gate and a runaway $1.00 run would pass. Add an explicit per-metric `direction` (`higher_is_better` default when absent, so the three existing rows are unaffected; `lower_is_better` for cost), using the repo's own precedent in `scripts/measure_perf_baseline.py` — `threshold = mean + sigma*stdev`, documented as "the mean − sigma * stdev shape but inverted sign per Decision 1". Teach compute_stats and write_thresholds_json to emit direction for every metric and to produce the cost row itself: the writer rebuilds the entire payload from stats_by_metric, so any hand-added row is destroyed by the next `--thresholds-out` run, which is the exact command the gate's failure comment tells maintainers to run. Add the cost regex to the stdout patterns, since that script scrapes printed output rather than the JSON dump. Make `extract_metrics` omit a metric whose measured value is None, the same way it already omits mean_faithfulness on a retrieval-only dump. Then fix the two CI breakages a newly-required metric causes: extend benchmark.yml's retrieval-only SKIP_ARGS with the cost metric, and add the cost field to smoke_check_gate.sh's synthetic dumps plus a fourth case asserting that a null-cost dump exits 0 with --skip-metric and 2 without it.</objective>
  <files-to-modify>
    <file path="scripts/check_thresholds.py">Read a per-metric direction and compare accordingly; treat a None measured value as absent rather than as 0.0; keep the exit 0/1/2 contract and the failure-comment format unchanged for higher-is-better metrics.</file>
    <file path="scripts/measure_baseline_variance.py">Per-metric direction in compute_stats (mean + sigma*stdev for lower-is-better), direction emitted by write_thresholds_json for every row, and the cost regex added to the stdout patterns with the in-file sync comment updated.</file>
    <file path="scripts/smoke_check_gate.sh">Add the cost field to the synthetic good/bad/broken dumps and a fourth case for the null-cost-plus-skip-metric path.</file>
    <file path=".github/workflows/benchmark.yml">Extend the retrieval-only SKIP_ARGS so an ordinary PR does not exit 2 against a thresholds file that carries a cost row.</file>
    <file path="tests/unit/test_check_thresholds.py">Cover a lower-is-better metric failing high and passing low, the absent-direction default, and a None measured value.</file>
    <file path="tests/unit/test_measure_baseline_variance.py">Cover the inverted threshold arithmetic, the direction field in the written payload, and the cost regex against a real printed benchmark line.</file>
  </files-to-modify>
  <validation>
    <check>`python -c "import sys; sys.path.insert(0,'scripts'); import check_thresholds as ct; d={'retrieval':{'k':3,'precision_at_1':1.0,'recall_at_k':1.0,'cost':{'cost_per_successful_query_usd':0.5}},'queries_path':'tests/golden/queries.yaml'}; t={'metrics':{'cost_per_successful_query_usd':{'threshold':0.01,'direction':'lower_is_better'}}}; f,v=ct.check(d,t,verify_queries_sha256=False); assert f and not v"` exits 0. RED before (the measured 0.5 passes a 0.01 threshold under the current comparison), GREEN after.</check>
    <check>The same call with `cost_per_successful_query_usd: 0.001` returns no failures.</check>
    <check>`bash scripts/smoke_check_gate.sh` exits 0.</check>
    <check>`uv run pytest tests/unit/test_check_thresholds.py tests/unit/test_measure_baseline_variance.py -q` passes.</check>
    <check>`python scripts/measure_baseline_variance.py --runs 10 --thresholds-out /tmp/t.json` then `python -c "import json; m=json.load(open('/tmp/t.json'))['metrics']; assert all('direction' in v for v in m.values()); assert m['precision_at_1']['threshold']==0.975"` — every row carries a direction and the existing higher-is-better arithmetic is unchanged.</check>
    <check>`python -c "import yaml; w=yaml.safe_load(open('.github/workflows/benchmark.yml')); s=[st for j in w['jobs'].values() for st in j['steps'] if st.get('id')=='check'][0]; assert 'cost_per_successful_query_usd' in s['run']"` exits 0.</check>
  </validation>
  <risks>
    <risk severity="high">This edits the comparison at the centre of the merge gate. A direction bug in the wrong place inverts an existing metric and lets a real precision regression merge green, with no visible failure to investigate. A human must read the check() diff and confirm the three existing rows still gate in the same direction, using the threshold-arithmetic check above.</risk>
    <risk severity="medium">smoke_check_gate.sh runs with `if: always()` on every PR. If the synthetic dumps are updated but the thresholds file gains a cost row in a different commit, the good-dump assertion starts exiting 2 and every PR fails on unrelated grounds.</risk>
    <risk severity="medium">Locking a real cost row requires ≥10 benchmark runs with --with-faithfulness, which is 2 LLM calls per query per run of genuine spend. Until a maintainer does that deliberately, thresholds.json carries no cost row and the gate is unchanged.</risk>
  </risks>
  <dependencies>
    <dep>T5</dep>
  </dependencies>
</task>

<task id="T7" name="Add --max-cost and a per-PR cost delta comment">
  <objective>Add `--max-cost` to benchmark.py mirroring `--min-precision`: a float argument, a post-run comparison, a FAIL line to stderr naming measured and gate, and `return 1`. Two behaviours the mirror must get right. First, on a retrieval-only run the cost is None, so `--max-cost` is a no-op that prints a notice to stderr naming `--with-faithfulness` as the way to make it enforceable — comparing None against a float is the bug this flag will otherwise ship with. Second, the existing precision gate returns 1 before the `--json` dump is written, so a failing precision run leaves no artifact; make the cost gate fire after the dump instead, so a cost failure still produces something to compare against, and record that deliberate divergence in decisions.md. For the PR comment, do not extend benchmark.yml's existing gate comment: `format_failure_comment` raises ValueError on an empty failure list by design ("callers should skip commenting on a green run") and its workflow step is gated on `rc == '1'`, so there is no green-run comment to add a delta to. Build `scripts/format_cost_delta.py` on `scripts/format_perf_delta.py`'s pattern — its own COMMENT_MARKER, a MetricComparison dataclass with delta_pct and status in ok/regression/new, alphabetical ordering for byte-stable output, pure stdlib, exit 0/1/2 — and add an advisory `cost-delta` job to benchmark.yml that posts with `always()`, including the static fallback body for the case where cost was not measured at all.</objective>
  <files-to-create>
    <file path="scripts/format_cost_delta.py">Renders the per-PR cost delta comment against the locked baseline; own marker, ok/regression/new per metric, static fallback when cost is unmeasured.</file>
    <file path="tests/unit/test_format_cost_delta.py">Golden-comment test alongside test_format_perf_delta.py: marker present, alphabetical ordering, no timestamps or hostnames, and the unmeasured-fallback body.</file>
  </files-to-create>
  <files-to-modify>
    <file path="src/attune_rag/benchmark.py">Add --max-cost, its None-safe no-op path with a stderr notice, and its post-dump gate placement.</file>
    <file path=".github/workflows/benchmark.yml">Add the advisory cost-delta job: measure, format, post-or-update by marker with always(), and a $GITHUB_STEP_SUMMARY block on green.</file>
    <file path="tests/unit/test_benchmark.py">Cover --max-cost as a no-op on a retrieval-only run and as a gate on a measured run, and that the JSON artifact exists after a cost failure.</file>
    <file path="docs/specs/cost-in-quality-gate/decisions.md">Record the post-dump gate placement and why it diverges from --min-precision.</file>
  </files-to-modify>
  <validation>
    <check>`python -m attune_rag.benchmark --max-cost 0.01; echo $?` prints 0 and a stderr notice that cost was not measured on this run. RED before (`unrecognized arguments: --max-cost`, exit 2), GREEN after.</check>
    <check>`python scripts/format_cost_delta.py --current /tmp/cur.json --baseline docs/specs/release-quality-baseline/thresholds.json --comment-out /tmp/c.md && grep -c 'attune-rag-cost-gate' /tmp/c.md` returns at least 1.</check>
    <check>Running format_cost_delta.py twice on the same inputs produces byte-identical output: `python scripts/format_cost_delta.py --current /tmp/cur.json --comment-out /tmp/a.md && python scripts/format_cost_delta.py --current /tmp/cur.json --comment-out /tmp/b.md && diff /tmp/a.md /tmp/b.md` exits 0.</check>
    <check>`python -c "import yaml; w=yaml.safe_load(open('.github/workflows/benchmark.yml')); assert 'cost-delta' in w['jobs']"` exits 0, and the comment step's `if:` contains `always()`.</check>
    <check>`uv run pytest tests/unit/test_format_cost_delta.py tests/unit/test_benchmark.py -q` passes.</check>
  </validation>
  <risks>
    <risk severity="medium">On this repo's default state ANTHROPIC_API_KEY is absent from Secrets, so the cost-delta comment will say "not measured" on every PR until a key is configured. That is the honest output, but it must read as a configuration gap rather than as a measurement of zero.</risk>
    <risk severity="medium">Comparing a None cost against a float --max-cost raises TypeError inside the gate, which the workflow's retry wrapper would report as a transient benchmark failure and mark the run inconclusive — a gate failure that looks like flake.</risk>
    <risk severity="low">A second PR comment marker means two bot comments per PR. The perf gate already does this, so the precedent holds, but the markers must not collide.</risk>
  </risks>
  <dependencies>
    <dep>T6</dep>
  </dependencies>
</task>

<task id="T8" name="Republish the README frontier and close out the docs">
  <objective>Publish the cost/quality frontier, with measured numbers only. The brief asks for a cost column on the lightweight-vs-transformer rows; those rows do not exist. README.md's hero table (lines 13-17) is metrics-as-rows by corpus-as-columns, and "lightweight" and "transformer" appear as annotations inside cells. The tier contrast lives in the "Two ways to run it" block below it. Either restructure the hero table into a tier-per-row frontier with precision@1, recall@3 and cost-per-successful-query as columns, or add the frontier table to the "Two ways to run it" section — and state in the PR which you did and why. Every figure must be reproducible from a committed artifact, footnoted in the existing `<sub>` style with the measurement conditions and the PRICE_TABLE_DATED stamp; prices change, so a dated figure is the only honest one. If no cost has been measured at the time of this task, the table ships with the cost column marked not yet measured and the command that produces it — an invented number here would undo the whole plan. Update the "Quality baselines" threshold table (~lines 464-468) with the cost row and its direction, and fix the dangling link at ~line 474: README points at docs/specs/release-quality-baseline/baseline-1.md, but that directory contains only thresholds.json and baseline-1.md lives under docs/specs/archive/release-quality-baseline/. Finish the [Unreleased] entries in both CHANGELOGs and mark the spec's tasks.md done.</objective>
  <files-to-create>
    <file path="docs/specs/cost-in-quality-gate/cost-baseline.md">The measured cost figures, the conditions they were measured under, the price-table date, and the exact command that reproduces them — the artifact every README number cites.</file>
  </files-to-create>
  <files-to-modify>
    <file path="README.md">Publish the tier-per-row cost/quality frontier, add the cost row and its direction to the Quality baselines table, and repoint the baseline-1.md link at docs/specs/archive/release-quality-baseline/.</file>
    <file path="CHANGELOG.md">Complete the `## [Unreleased]` entries for the cost fields, the gate direction, the --max-cost flag, and the cost delta comment, each with its surface impact stated.</file>
    <file path="../attune-ai/CHANGELOG.md">Complete the `## [Unreleased]` entry for the price-table move and the session_summarizer reconciliation.</file>
    <file path="docs/specs/cost-in-quality-gate/tasks.md">Mark T1-T8 done with the commits that closed them.</file>
  </files-to-modify>
  <validation>
    <check>`grep -n 'docs/specs/release-quality-baseline/baseline-1.md' README.md` returns nothing, and `grep -c 'archive/release-quality-baseline/baseline-1.md' README.md` returns at least 1. RED before (the dangling link is live), GREEN after.</check>
    <check>Every dollar figure in README.md appears in docs/specs/cost-in-quality-gate/cost-baseline.md: `for v in $(grep -oE '\$[0-9]+\.[0-9]+' README.md | sort -u); do grep -qF "$v" docs/specs/cost-in-quality-gate/cost-baseline.md || echo "UNSOURCED $v"; done` prints nothing.</check>
    <check>The README cost footnote contains the same date string as `python -c "from attune_rag.pricing import PRICE_TABLE_DATED; print(PRICE_TABLE_DATED)"`.</check>
    <check>`python -c "import re,sys; t=open('README.md').read(); assert 'cost' in t.lower().split('two ways to run it')[1][:2000].lower()"` — the tier contrast section carries the cost signal.</check>
    <check>`uv run pytest tests/unit -q` passes and `uv run pytest tests/unit --cov -q` stays at or above the fail_under=77 gate.</check>
  </validation>
  <risks>
    <risk severity="medium">Publishing a cost figure that was not measured, or that came from a different runner than the quality numbers beside it, makes the frontier table a claim rather than a measurement — the same failure the economics half of the thesis already has.</risk>
    <risk severity="low">Restructuring the hero table changes the first thing a reader sees. If the frontier is added below instead, the hero table's transformer-tier annotations must not contradict it.</risk>
  </risks>
  <dependencies>
    <dep>T7</dep>
  </dependencies>
</task>

---

## Reference

Paths are relative to the attune-rag repository root. Paths beginning `../attune-ai/` are the sibling repository; both are checked out side by side.

**The gap**
- `src/attune_rag/benchmark.py` — 1067 lines. `_run_benchmark(queries, k, corpus, retriever)` returns `retriever`, `corpus`, `total_queries`, `precision_at_1`, `recall_at_k`, `k`, `mean_latency_ms`, `max_latency_ms`, `by_difficulty`, `per_query`. Docstring: "Pure: no LLM calls, no disk writes. Spends only the cost of retrieval (CPU-bound for `KeywordRetriever`)." `_score_faithfulness` (line 400) is the only token-spending path: `pipeline.run_and_generate` plus `judge.score`, 2 LLM calls per query, behind `--with-faithfulness`. `main()` gates at line 912 with `if report["precision_at_1"] < args.min_precision: return 1`, before the retrieval-only `--json` dump at line 924. `_dump_json` (line 602) writes `indent=2, sort_keys=True, encoding="utf-8"`.
- `docs/specs/release-quality-baseline/thresholds.json` — 576 bytes, the only file in that directory. `commit`, `measured_at`, `metrics` (`mean_faithfulness` 0.9698, `precision_at_1` 0.975, `recall_at_3` 1.0, each `{mean, stdev, threshold}`), `queries_path`, `queries_sha256`, `runs` 20, `sigma` 2.0.

**The move being mirrored**
- `src/attune_rag/model_tiers.py` — canonical, stdlib-only (logging, os, typing), docstring carrying the ownership narrative and the 2026-04-30 core-dependency date, no licence header.
- `../attune-ai/src/attune/model_tiers.py` — lazy re-export: thin wrappers with function-local imports, `_LAZY_NAMES`, PEP 562 `__getattr__`, `__dir__`, TYPE_CHECKING-only imports, Apache header.
- `tests/unit/test_model_tiers.py` and `../attune-ai/tests/unit/test_model_tiers.py` — the twin-test precedent.
- `../attune-ai/pyproject.toml:89` — `"attune-rag>=1.2.0,<2.0"` as a core (non-optional) dependency, with the inline rationale that confirms the direction of travel.

**The real price table, and its consumers**
- `../attune-ai/src/attune/models/registry.py` — `ModelInfo` (frozen, with `to_router_config` / `to_workflow_config` / `to_cost_tracker_pricing`), `ModelTier`, `ModelProvider`, `MODEL_REGISTRY`, `ADDITIONAL_MODELS`, `TIER_PRICING` at the tail, and the dated-price-in-a-comment at line 524: `# Sonnet 5 pricing (std; intro $2/$10 until 2026-08-31)`.
- `../attune-ai/src/attune/cost_tracker.py:27-28, 34-67, 71` — imports, `_build_model_pricing()`, and the eager `MODEL_PRICING`. Lines 54-59 carry the price-history rule that `attune_rag/pricing.py`'s docstring lifts.
- Module-scope consumers to keep off the heavy import: `../attune-ai/src/attune/agents/release/base_agent.py:22`, `../attune-ai/src/attune/routing/model_router.py:31`, `../attune-ai/src/attune/workflows/config.py:28-29`, `../attune-ai/src/attune/workflows/step_config.py:15`, `../attune-ai/src/attune/workflows/base.py:41`.
- Function-local cost-from-usage idiom to follow: `../attune-ai/src/attune/telemetry/usage_tracker.py:991` and `../attune-ai/src/attune/llm/providers/anthropic.py:336`.
- The fourth, drifting copy: `../attune-ai/src/attune/ops/session_summarizer.py:42-48`.

**Gate prior art**
- `scripts/measure_perf_baseline.py` — `DEFAULT_SIGMA = 2.0`, `threshold = round(mean + sigma*stdev, 6)`, documented as "the `mean − sigma * stdev` shape but inverted sign per Decision 1". The correct shape for a lower-is-better threshold.
- `docs/specs/downstream-validation/perf-thresholds.json` — the upper-bound thresholds payload, including the `environment` block that matters for cost the same way it matters for latency.
- `scripts/format_perf_delta.py` — `COMMENT_MARKER = "<!-- attune-rag-perf-gate -->"`, `MetricComparison` with `delta_pct` and `status` in ok/regression/new, alphabetical ordering, pure stdlib, posts on green runs. The model for `scripts/format_cost_delta.py`.
- `.github/workflows/perf.yml` — the `delta-check` job: measure, format, post-or-update with `always()`. The model for benchmark.yml's new advisory job.
- `scripts/check_thresholds.py` — `extract_metrics`, `check() -> (failures, validation_errors)`, `--skip-metric`, `COMMENT_MARKER = "<!-- attune-rag-quality-gate -->"`, `format_failure_comment` raising ValueError on an empty list.
- `scripts/measure_baseline_variance.py:44-58` — `_PERCENT_PATTERNS` / `_FLOAT_PATTERNS` with the in-file comment "Keep these in sync with `_print_summary` and `_print_faithfulness`"; `compute_stats` at line 84; `write_thresholds_json` at line 197, which rebuilds the whole payload.
- `scripts/smoke_check_gate.sh` — synthetic good/bad/broken dumps, run with `if: always()` on every PR.
- `.github/workflows/benchmark.yml` — the `gate` job, the `mode` step, the retrieval-only `SKIP_ARGS`, the comment step gated on `steps.check.outputs.rc == '1'`, and the "Fail on validation error" step.

**Token plumbing prior art (sibling package)**
- `../attune-forms/benchmarks/provider.py:22-23, 182-195` — `tokens_input` / `tokens_output` on the reply dataclass, and a raise rather than a zero-default when usage is absent.
- `../attune-forms/benchmarks/outcome_report.py` — "Descriptive task outcomes and costs with missingness and matched-pair counts"; `planned` / `attempted` counts so missing runs are explicit rather than silently averaged. The shape to copy for cost-vs-success reporting.

**Surfaces this touches**
- `src/attune_rag/providers/base.py` — `CitationDocument`, `CitedResponse(text, claim_citations)`, the `LLMProvider` Protocol. `attune_rag.providers.__all__` is `{LLMProvider, get_provider, list_available}` and does not need to change; `tests/unit/test_contracts.py` and `tests/unit/providers/` do.
- `src/attune_rag/eval/faithfulness.py:139` — `FaithfulnessResult` (frozen, with `to_dict()`); `FaithfulnessJudge.score` at line 255 routes API or subscription via `auth_mode`.
- `src/attune_rag/pipeline.py:67` — `RagResult` (frozen, defaulted `claim_citations` / `used_native_citations`); `run_and_generate` at line 375.
- `README.md` — hero table at lines 13-17, footnotes at 28-31, "Two ways to run it" at 33-46, "Quality baselines" at ~455-485, dangling `baseline-1.md` link at ~474 (the file is at `docs/specs/archive/release-quality-baseline/baseline-1.md`).
- House spec-dir shape: `docs/specs/alias-overlap-remediation/` (README, requirements, design, tasks, decisions, risks).