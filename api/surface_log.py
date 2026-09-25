"""Minimal catalog exposure log.

Each line is {"item_id", "surface_via", "ts"}. surface_via is one of
propose_styles, list_catalog, or route. Weekly review lists items that were
not surfaced in two consecutive weeks, which is the input for keep-or-drop.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

SURFACES = ("propose_styles", "list_catalog", "route")


def log_path(explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        return explicit
    override = (os.environ.get("SURFACE_LOG_PATH") or "").strip()
    if override:
        return Path(override)
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return None
    data = Path(os.environ.get("SITE_COLLECTION_DATA", ".")).expanduser()
    return data / "logs" / "surface.jsonl"


def record_surface(
    item_ids: Iterable[str],
    surface_via: str,
    *,
    ts: datetime | None = None,
    path: Path | None = None,
    explore_ids: Iterable[str] | None = None,
) -> int:
    """Append one impression per item. Failures never affect the caller."""
    if surface_via not in SURFACES:
        return 0
    destination = log_path(path)
    if destination is None:
        return 0
    moment = (ts or datetime.now(timezone.utc)).astimezone(timezone.utc)
    stamp = moment.isoformat()
    explore = {str(item).strip() for item in (explore_ids or []) if str(item).strip()}
    seen: list[str] = []
    for raw in item_ids:
        item_id = str(raw or "").strip()
        if item_id and item_id not in seen:
            seen.append(item_id)
    if not seen:
        return 0
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("a", encoding="utf-8") as handle:
            for item_id in seen:
                row = {"item_id": item_id, "surface_via": surface_via, "ts": stamp}
                if item_id in explore:
                    row["explore"] = True
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        return 0
    return len(seen)


def _ids_from_mappings(rows: Iterable[dict[str, Any]], *keys: str) -> list[str]:
    found: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in keys:
            item_id = str(row.get(key) or "").strip()
            if item_id and item_id not in found:
                found.append(item_id)
                break
    return found


def ids_from_catalog(payload: dict[str, Any]) -> list[str]:
    return _ids_from_mappings(payload.get("items") or [], "id", "item_id")


def ids_from_route(payload: dict[str, Any]) -> list[str]:
    found = _ids_from_mappings(payload.get("source_references") or [], "item_id", "id")
    for row in payload.get("optional_provider_routes") or []:
        item_id = str((row or {}).get("item_id") or "").strip()
        if item_id and item_id not in found:
            found.append(item_id)
    for row in payload.get("paid_provider_options") or []:
        item_id = str((row or {}).get("item_id") or "").strip()
        if item_id and item_id not in found:
            found.append(item_id)
    for pattern in payload.get("self_patterns") or []:
        for credit in (pattern or {}).get("source_credits") or []:
            item_id = str((credit or {}).get("item_id") or "").strip()
            if item_id and item_id not in found:
                found.append(item_id)
    return found


def ids_from_proposal(payload: dict[str, Any]) -> list[str]:
    found, _explore = _proposal_ids(payload)
    return found


def explore_ids_from_proposal(payload: dict[str, Any]) -> list[str]:
    _found, explore = _proposal_ids(payload)
    return explore


def _proposal_ids(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    found: list[str] = []
    explore: list[str] = []
    for direction in payload.get("directions") or []:
        for row in (direction or {}).get("reference_items") or []:
            item_id = str((row or {}).get("id") or (row or {}).get("item_id") or "").strip()
            if not item_id:
                continue
            if item_id not in found:
                found.append(item_id)
            if row.get("explore") and item_id not in explore:
                explore.append(item_id)
    return found, explore


def read_events(path: Path | None = None) -> list[dict[str, Any]]:
    destination = log_path(path)
    if destination is None or not destination.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in destination.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("surface_via") in SURFACES and row.get("item_id") and row.get("ts"):
            events.append(row)
    return events


def week_start(moment: datetime) -> datetime:
    moment = moment.astimezone(timezone.utc)
    monday = moment.date() - timedelta(days=moment.weekday())
    return datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)


def weekly_surface_report(
    catalog_ids: Iterable[str],
    *,
    as_of: datetime | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    """Count impressions in the current week and the week before it.

    zero_for_two_weeks is empty until the log actually covers the start of
    the earlier week. A brand-new log must not mark the whole catalog unseen.
    """
    moment = (as_of or datetime.now(timezone.utc)).astimezone(timezone.utc)
    current = week_start(moment)
    previous = current - timedelta(days=7)
    windows = (previous, current)
    counts = {start.strftime("%G-W%V"): {} for start in windows}
    explore_counts = {start.strftime("%G-W%V"): {} for start in windows}
    earliest: datetime | None = None
    for event in read_events(path):
        try:
            when = datetime.fromisoformat(event["ts"])
        except ValueError:
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        when = when.astimezone(timezone.utc)
        earliest = when if earliest is None else min(earliest, when)
        start = week_start(when)
        label = start.strftime("%G-W%V")
        if label not in counts:
            continue
        bucket = counts[label]
        bucket[event["item_id"]] = bucket.get(event["item_id"], 0) + 1
        if event.get("explore"):
            explore_counts[label][event["item_id"]] = explore_counts[label].get(event["item_id"], 0) + 1
    ready = earliest is not None and earliest <= previous
    unseen: list[str] = []
    if ready:
        for item_id in catalog_ids:
            if all(counts[start.strftime("%G-W%V")].get(item_id, 0) == 0 for start in windows):
                unseen.append(item_id)
    weeks = []
    for start in windows:
        label = start.strftime("%G-W%V")
        weeks.append({
            "week": label,
            "start": start.date().isoformat(),
            "counts": counts[label],
            "explore_counts": explore_counts[label],
            "total": sum(counts[label].values()),
        })
    return {
        "weeks": weeks,
        "zero_for_two_weeks": unseen,
        "review_ready": ready,
    }
