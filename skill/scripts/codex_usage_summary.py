#!/usr/bin/env python3
"""Summarize local Codex token and model metadata without reading chat text.

Token aggregation is derived from huajiexiewenfeng/codex-token-usage-skill
(MIT). See references/third-party.md.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import pathlib
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


UUID = re.compile(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")


def session_id(path: pathlib.Path) -> str:
    match = UUID.search(path.name)
    return match.group(1) if match else path.stem


def session_paths(codex_home: pathlib.Path):
    for name in ("sessions", "archived_sessions"):
        root = codex_home / name
        if root.exists():
            yield from root.rglob("*.jsonl")


def timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def summarize(codex_home: pathlib.Path, days: int, timezone: ZoneInfo) -> dict[str, object]:
    cutoff = datetime.now(timezone) - timedelta(days=days)
    seen_tokens: set[tuple[object, ...]] = set()
    models: collections.Counter[str] = collections.Counter()
    reasoning: collections.Counter[str] = collections.Counter()
    tiers: collections.Counter[str] = collections.Counter()
    session_turns: collections.Counter[str] = collections.Counter()
    sessions: set[str] = set()
    archived: set[str] = set()
    token_totals = collections.Counter()

    for path in session_paths(codex_home):
        sid = session_id(path)
        recent = False
        local_models: collections.Counter[str] = collections.Counter()
        local_reasoning: collections.Counter[str] = collections.Counter()
        local_tiers: collections.Counter[str] = collections.Counter()
        try:
            handle = path.open("r", encoding="utf-8", errors="replace")
        except OSError:
            continue
        with handle:
            for line in handle:
                if not any(marker in line for marker in ('"token_count"', '"task_started"', '"thread_settings_applied"')):
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                when = timestamp(obj.get("timestamp"))
                if when is None or when.astimezone(timezone) < cutoff:
                    continue
                recent = True
                payload = obj.get("payload") or {}
                kind = payload.get("type")
                if kind == "task_started":
                    session_turns[sid] += 1
                elif kind == "thread_settings_applied":
                    settings = payload.get("thread_settings") or {}
                    local_models[settings.get("model") or "unknown"] += 1
                    local_reasoning[settings.get("reasoning_effort") or "unknown"] += 1
                    local_tiers[settings.get("service_tier") or "unknown"] += 1
                elif kind == "token_count":
                    usage = ((payload.get("info") or {}).get("last_token_usage") or {})
                    key = (sid, obj.get("timestamp"), usage.get("total_tokens"), usage.get("input_tokens"), usage.get("output_tokens"))
                    if not usage or key in seen_tokens:
                        continue
                    seen_tokens.add(key)
                    for field in ("total_tokens", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
                        token_totals[field] += int(usage.get(field) or 0)
        if recent:
            sessions.add(sid)
            if "archived_sessions" in path.parts:
                archived.add(sid)
            models[local_models.most_common(1)[0][0] if local_models else "unknown"] += 1
            reasoning[local_reasoning.most_common(1)[0][0] if local_reasoning else "unknown"] += 1
            tiers[local_tiers.most_common(1)[0][0] if local_tiers else "unknown"] += 1

    input_tokens = token_totals["input_tokens"]
    cached = token_totals["cached_input_tokens"]
    output = token_totals["output_tokens"]
    return {
        "window_days": days,
        "sessions": len(sessions),
        "archived_sessions": len(archived),
        "token_events": len(seen_tokens),
        "tokens": {
            "total": token_totals["total_tokens"],
            "input": input_tokens,
            "cached_input": cached,
            "output": output,
            "reasoning_output": token_totals["reasoning_output_tokens"],
            "net": input_tokens - cached + output,
            "cache_hit_rate": cached / input_tokens if input_tokens else 0,
        },
        "models": dict(models),
        "reasoning": dict(reasoning),
        "service_tiers": dict(tiers),
        "sessions_30_plus_turns": sum(turns >= 30 for turns in session_turns.values()),
        "coverage_note": "Local Codex JSONL metadata only; ChatGPT cloud metadata is not included.",
    }


def as_markdown(report: dict[str, object]) -> str:
    tokens = report["tokens"]
    return "\n".join(
        [
            "# Weekly model usage check",
            "",
            f"Window: {report['window_days']} days",
            f"Codex sessions: {report['sessions']} ({report['archived_sessions']} archived)",
            f"Total tokens: {tokens['total']:,}",
            f"Net tokens: {tokens['net']:,}",
            f"Cache hit rate: {tokens['cache_hit_rate']:.2%}",
            f"Models: {report['models']}",
            f"Reasoning: {report['reasoning']}",
            f"Service tiers: {report['service_tiers']}",
            f"Sessions with 30+ turns: {report['sessions_30_plus_turns']}",
            "",
            f"Coverage: {report['coverage_note']}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME") or str(pathlib.Path.home() / ".codex"))
    parser.add_argument("--days", type=int, default=8)
    parser.add_argument("--timezone", default=None)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    timezone = ZoneInfo(args.timezone) if args.timezone else datetime.now().astimezone().tzinfo
    report = summarize(pathlib.Path(args.codex_home).expanduser(), args.days, timezone)
    print(json.dumps(report, indent=2) if args.format == "json" else as_markdown(report))


if __name__ == "__main__":
    main()
