#!/usr/bin/env python3
"""Build a labelling sheet from Claude Code session transcripts.

The experiment this feeds: does retrieval quality predict whether a session
actually went well? Nothing currently records that, so the first step is a
hand-labelled sample.

Read-only. Touches nothing but its own output file, makes no network calls,
and never modifies a transcript.

Two modes:

    python3 extract_sessions.py --discover
        Report what is actually in your transcripts: which hooks fire, what
        context they inject, whether an attune digest is captured at all.
        Run this FIRST. The extract mode guesses at the digest marker; this
        tells you whether the guess is right.

    python3 extract_sessions.py --limit 40 --out sessions.csv
        Write one row per session to a CSV, with an empty `went_well` column
        for you to fill in. Open it in a spreadsheet, sort, type a number.

Why a CSV: filling one column in a spreadsheet is a mouse job.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Substrings that suggest an attune memory digest was injected. Deliberately
# broad — --discover reports what actually matched so you can narrow it.
DIGEST_HINTS = (
    "recall_digest",
    "attune.memory",
    "curated",
    "FCALL",
    ".attune",
)


def _iter_records(path: Path):
    """Yield parsed JSON records, skipping malformed lines.

    Transcripts are appended live, so the last line can be a partial write.
    A malformed line is skipped and counted rather than aborting the file.
    """
    bad = 0
    with path.open(errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                bad += 1
    if bad:
        print(f"  note: {bad} unparseable line(s) in {path.name}", file=sys.stderr)


def _text_of(message: object) -> str:
    """Flatten a message's content to plain text."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(parts)
    return ""


def _first_real_prompt(records: list[dict]) -> str:
    """The first user message that is a person talking, not injected context.

    System reminders, hook output and environment snapshots all arrive as
    user-role records. They are filtered here so the sheet shows what the
    session was actually about.
    """
    for rec in records:
        if rec.get("type") != "user":
            continue
        text = _text_of(rec.get("message")).strip()
        if not text or text.startswith("<system-reminder"):
            continue
        if text.startswith("<") and text.endswith(">"):
            continue
        return " ".join(text.split())
    return ""


def _duration_minutes(records: list[dict]) -> float | None:
    stamps = []
    for rec in records:
        raw = rec.get("timestamp")
        if not raw:
            continue
        try:
            stamps.append(datetime.fromisoformat(str(raw).replace("Z", "+00:00")))
        except ValueError:
            continue
    if len(stamps) < 2:
        return None
    return round((max(stamps) - min(stamps)).total_seconds() / 60, 1)


def _hook_context(records: list[dict]) -> tuple[list[str], str]:
    """Return (hook commands that fired, all context they injected)."""
    commands: list[str] = []
    injected: list[str] = []
    for rec in records:
        if rec.get("type") != "system":
            continue
        for info in rec.get("hookInfos") or []:
            if isinstance(info, dict) and info.get("command"):
                commands.append(str(info["command"]))
        for ctx in rec.get("hookAdditionalContext") or []:
            injected.append(ctx if isinstance(ctx, str) else json.dumps(ctx))
    return commands, "\n".join(injected)


def _attachment_text(records: list[dict]) -> str:
    """Text of every attachment's rendered content."""
    out = []
    for rec in records:
        if rec.get("type") != "attachment":
            continue
        for block in rec.get("rendered") or []:
            if isinstance(block, dict) and block.get("content"):
                out.append(str(block["content"]))
    return "\n".join(out)


def summarize(path: Path) -> dict:
    records = list(_iter_records(path))
    if not records:
        return {}

    commands, hook_ctx = _hook_context(records)
    attach_txt = _attachment_text(records)
    haystack = hook_ctx + "\n" + attach_txt

    matched = sorted({h for h in DIGEST_HINTS if h in haystack})

    tool_calls = 0
    tool_errors = 0
    for rec in records:
        message = rec.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                tool_calls += 1
            if block.get("type") == "tool_result" and block.get("is_error"):
                tool_errors += 1

    first = records[0]
    # gitBranch/cwd can be empty on the opening record (the branch is not
    # always known yet), so take the most common non-empty value instead.
    def _common(field: str) -> str:
        vals = Counter(
            str(r.get(field)) for r in records if str(r.get(field) or "").strip()
        )
        return vals.most_common(1)[0][0] if vals else ""

    return {
        "session_id": first.get("sessionId", path.stem),
        "started": (first.get("timestamp") or "")[:19],
        "cwd": _common("cwd"),
        "branch": _common("gitBranch"),
        "user_turns": sum(1 for r in records if r.get("type") == "user"),
        "assistant_turns": sum(1 for r in records if r.get("type") == "assistant"),
        "tool_calls": tool_calls,
        "tool_errors": tool_errors,
        "duration_min": _duration_minutes(records),
        "digest_present": "yes" if matched else "no",
        "digest_markers": ";".join(matched),
        "digest_chars": len(hook_ctx),
        "hooks_fired": ";".join(sorted(set(commands))),
        "first_prompt": _first_real_prompt(records)[:200],
        # You fill these in:
        "went_well": "",
        "memory_helped": "",
        "notes": "",
        "_path": str(path),
    }


def discover(sessions: list[Path]) -> None:
    print(f"Scanning {len(sessions)} transcript(s)\n")
    hooks: Counter = Counter()
    subtypes: Counter = Counter()
    markers: Counter = Counter()
    with_ctx = 0
    samples: list[str] = []

    for path in sessions:
        records = list(_iter_records(path))
        commands, ctx = _hook_context(records)
        hooks.update(commands)
        subtypes.update(
            r.get("subtype", "?") for r in records if r.get("type") == "system"
        )
        if ctx.strip():
            with_ctx += 1
            if len(samples) < 2:
                samples.append(ctx[:600])
        blob = ctx + "\n" + _attachment_text(records)
        markers.update(h for h in DIGEST_HINTS if h in blob)

    print("Hooks that fired:")
    for cmd, n in hooks.most_common(15) or [("(none)", 0)]:
        print(f"  {n:4}x  {cmd}")

    print("\nsystem-record subtypes:")
    for st, n in subtypes.most_common(10) or [("(none)", 0)]:
        print(f"  {n:4}x  {st}")

    print(f"\nSessions where a hook injected context: {with_ctx}/{len(sessions)}")

    print("\nDigest-marker hits (these decide whether extract mode can see it):")
    if markers:
        for m, n in markers.most_common():
            print(f"  {n:4}x  {m}")
    else:
        print("  NONE. No attune digest is visible in these transcripts.")
        print("  That is itself the finding: if the digest is not captured,")
        print("  the correlation cannot be measured from transcripts alone.")

    for i, s in enumerate(samples, 1):
        print(f"\n--- injected-context sample {i} (first 600 chars) ---\n{s}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projects-dir", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--project", default="", help="substring filter on the project folder")
    ap.add_argument("--limit", type=int, default=40, help="most recent N sessions")
    ap.add_argument("--min-turns", type=int, default=3,
                    help="skip trivially short sessions (default 3 user turns)")
    ap.add_argument("--out", default="sessions.csv")
    ap.add_argument("--discover", action="store_true",
                    help="report what is in the transcripts; write nothing")
    args = ap.parse_args()

    root = Path(args.projects_dir).expanduser()
    if not root.is_dir():
        print(f"No transcripts at {root}", file=sys.stderr)
        return 1

    sessions = [
        p for p in root.glob("*/*.jsonl")
        if not args.project or args.project in p.parent.name
    ]
    sessions.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if not sessions:
        print(f"No .jsonl transcripts under {root}", file=sys.stderr)
        return 1

    if args.discover:
        discover(sessions[: max(args.limit, 20)])
        return 0

    rows = []
    for path in sessions:
        if len(rows) >= args.limit:
            break
        row = summarize(path)
        if row and row["user_turns"] >= args.min_turns:
            rows.append(row)

    if not rows:
        print("No sessions passed the filters.", file=sys.stderr)
        return 1

    fields = [k for k in rows[0] if k != "_path"]
    out = Path(args.out).expanduser()
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    n_digest = sum(1 for r in rows if r["digest_present"] == "yes")
    print(f"Wrote {len(rows)} session(s) to {out}")
    print(f"  digest detected in {n_digest}/{len(rows)}")
    if n_digest == 0:
        print("\n  WARNING: no digest detected in any session. Run --discover.")
        print("  Without it there is no retrieval side to correlate against,")
        print("  and the sheet only measures session outcomes.")
    print("""
Now fill two columns in a spreadsheet:

  went_well      1-5. Did the session reach a good outcome?
  memory_helped  1-5. Did what memory surfaced actually get used?

Label went_well WITHOUT looking at digest_present or digest_chars, or you
will score the thing you are trying to test. Sort by first_prompt, not by
any digest column.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
