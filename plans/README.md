# Phase 1 plan files

Drop these into `.claude/plans/` in the target repo and run `/spec`.

| Plan | Slug | Repo | Status |
|---|---|---|---|
| Cost joined to quality | `cost-in-quality-gate` | `attune-rag` | Verified, 8 tasks |
| Temporal staleness | `temporal-staleness` | `attune-ai` | Verified, 8 tasks |
| Deletion, proven end to end | `provable-deletion` | two repos | **Being split — do not execute** |

## Verification status

Each plan was authored from a fresh read of the source, then checked by three
adversarial lenses — ground truth on every path and symbol, `read_spec()` regex
conformance, and whether the gate can actually fail — and repaired.

| Plan | Defects found | Blocking | Repaired |
|---|---|---|---|
| `cost-in-quality-gate` | 39 | 7 | yes |
| `provable-deletion` | 41 | 8 | yes |
| `temporal-staleness` | 36 | 4 | yes |

An independent check afterwards, running the real
`_parse_tasks_from_xml` regexes and resolving every `path=` against the
filesystem, confirmed the cost and staleness plans parse cleanly with no
dangling `<dep>`, no bad severity value, and no path that fails to resolve.
Paths that appear missing in those two are spec files an earlier task in the
same plan creates — correct sequencing.

## The defect the lenses missed

`provable-deletion` spans `attune-rag` and `attune-ai`, and prefixed every path
with the repo name (`attune-rag/src/attune_rag/corpus/base.py`). That resolves
to nothing from either repo root, **and it fails silently**: the path contains
no `..`, so `attune/spec/workspace.py::_portable_path` accepts it and the
executor writes to the wrong location rather than raising.

The established pattern for cross-repo work in this family is a companion plan
file per repo — see `attune-ai/.claude/plans/extended-cache-ttl-siblings.md`,
which says outright *"Task B (separate repo, separate PR). Do not start in the
attune-ai session."* The plan is being split into `provable-deletion`
(attune-rag) and `curated-erasure` (attune-ai), with the cross-repo ordering
expressed as prose in the dependent objective plus a checkable precondition,
since `<dep>` cannot cross files.

## Cross-repo constraint worth remembering

`_portable_path` (`attune/spec/workspace.py:50-55`) raises
`CommandWorkspaceError` on any path containing `..`, and
`SpecArtifactReceipt.__post_init__` runs it on every artifact path. So neither
a `../other-repo/` path nor a repo-name prefix works. One plan file per repo is
the only shape that executes correctly.
