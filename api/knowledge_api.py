"""Text-only design patterns and source routing for the public MCP."""

from __future__ import annotations

import csv
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def _knowledge_root(data_root: Path) -> Path:
    return data_root / "knowledge"


@lru_cache(maxsize=4)
def _cached_patterns(directory: str, fingerprint: tuple[tuple[str, int], ...]) -> dict[str, dict[str, Any]]:
    root = Path(directory)
    schema = json.loads((root.parent / "pattern.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    patterns: dict[str, dict[str, Any]] = {}
    for filename, _ in fingerprint:
        pattern = json.loads((root / filename).read_text(encoding="utf-8"))
        validator.validate(pattern)
        Draft202012Validator.check_schema(pattern["props_schema"])
        if pattern["id"] != Path(filename).stem or pattern["id"] in patterns:
            raise ValueError(f"invalid or duplicate pattern ID: {filename}")
        patterns[pattern["id"]] = pattern
    return patterns


def load_patterns(data_root: Path) -> dict[str, dict[str, Any]]:
    directory = _knowledge_root(data_root) / "patterns"
    if not directory.is_dir():
        return {}
    fingerprint = tuple(sorted((path.name, path.stat().st_mtime_ns) for path in directory.glob("*.json")))
    return _cached_patterns(str(directory), fingerprint)


@lru_cache(maxsize=4)
def _cached_routes(path: str, mtime_ns: int) -> dict[str, dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    routes = {row["item_id"]: row for row in rows}
    if len(routes) != len(rows):
        raise ValueError("duplicate source route")
    return routes


def load_routes(data_root: Path) -> dict[str, dict[str, str]]:
    path = _knowledge_root(data_root) / "routes.csv"
    return _cached_routes(str(path), path.stat().st_mtime_ns)


def validate_repository(data_root: Path, source_items: list[dict[str, Any]], *, check_evidence: bool = True) -> dict[str, int]:
    patterns = load_patterns(data_root)
    routes = load_routes(data_root)
    source_by_id = {item["id"]: item for item in source_items}
    if set(routes) != set(source_by_id):
        raise ValueError("source routes must cover every catalog item exactly once")
    expected_patterns: dict[str, set[str]] = {item_id: set() for item_id in source_by_id}
    for pattern in patterns.values():
        for ref in pattern["source_refs"]:
            item = source_by_id.get(ref["item_id"])
            if item is None:
                raise ValueError(f"unknown source {ref['item_id']} in {pattern['id']}")
            expected_patterns[item["id"]].add(pattern["id"])
            root_path = (data_root / item["archive_path"]).resolve() if item.get("archive_path") else None
            for rel in ref["evidence_paths"]:
                if ref["item_id"] == "063" and not (rel.startswith("apps/ui/") or rel.startswith("apps/origin/") or rel == "LICENSING.md"):
                    raise ValueError("coss evidence must stay within the MIT subtree")
                if check_evidence and (root_path is None or not (root_path / rel).resolve().is_relative_to(root_path) or not (root_path / rel).is_file()):
                    raise ValueError(f"missing evidence {ref['item_id']}:{rel}")
    for item_id, route in routes.items():
        listed = {name.strip() for name in route["pattern_ids"].split(";") if name.strip()}
        if listed != expected_patterns[item_id]:
            raise ValueError(f"route pattern list is stale for {item_id}")
        if route["provider_status"] == "unofficial-not-routed" and "provider-direct" in route["route_modes"]:
            raise ValueError(f"unofficial provider route must remain manual: {item_id}")
    media_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".woff", ".woff2", ".ttf", ".mp4", ".mp3", ".wav", ".pdf", ".fig", ".psd"}
    for file_path in _knowledge_root(data_root).rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in media_suffixes:
            raise ValueError(f"media asset in public knowledge repository: {file_path}")
        if file_path.is_file() and file_path.suffix == ".json":
            body = file_path.read_text(encoding="utf-8").lower()
            if "data:image/" in body or "<img" in body:
                raise ValueError(f"embedded media in public knowledge repository: {file_path}")
    return {"patterns": len(patterns), "sources": len(routes)}


def source_credits(pattern: dict[str, Any], source_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["id"]: item for item in source_items}
    credits = []
    for ref in pattern["source_refs"]:
        item = by_id[ref["item_id"]]
        match = re.search(r"(?:^|[;；]\s*)commit=([^;；]+)", item.get("notes") or "")
        repo = re.search(r"(?:^|[;；]\s*)repo=(https?://[^;；]+)", item.get("notes") or "")
        credits.append({
            "item_id": item["id"], "project": item["title"], "credit": ref["credit"],
            "source_url": item["url"], "source_commit": match.group(1).strip() if match else None,
            "repository_url": repo.group(1).strip() if repo else item["url"],
            "catalog_license": item["license"], "license_scope": ref.get("license_scope") or item["license"],
            "evidence_paths": ref["evidence_paths"],
            "attribution": f"{ref['credit']} — {item['url']} ({ref.get('license_scope') or item['license']})",
        })
    return credits


USE_POLICY = "Implement fresh code in the user's stack. Cite these sources; do not copy or fetch third-party media."

# A Chinese brief should meet English pattern keywords, and the reverse.
QUERY_ALIASES: tuple[tuple[str, ...], ...] = (
    ("按钮", "button"),
    ("可访问", "无障碍", "accessible"),
    ("组件", "component"),
    ("渐变", "gradient"),
    ("窗口", "window", "dialog"),
    ("控件", "control"),
    ("自适应", "adaptive"),
    ("后台", "管理台", "dashboard"),
    ("图标", "icon"),
    ("动效", "动画", "motion"),
    ("游戏", "hud"),
    ("安全区", "safe area"),
)


def expand_query_terms(brief_lower: str, terms: set[str]) -> set[str]:
    expanded = set(terms)
    for group in QUERY_ALIASES:
        if any(alias in brief_lower for alias in group):
            expanded.update(group)
    return expanded


# Non-engineering briefs (a blog, a folded brochure) often share no keywords
# with pattern ids. Fall back to the nearest style instead of an empty list.
_AESTHETIC_HINTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("博客", "blog", "折页", "brochure", "杂志", "editorial", "编辑", "排版"), "编辑风"),
    (("落地页", "landing", "商店", "store", "shop", "电商", "商城"), "电商实感"),
    (("极简", "minimal"), "极简克制"),
    (("玻璃", "glass", "液态"), "玻璃拟态"),
    (("拟物", "skeu"), "拟物质感"),
    (("游戏", "hud", "科幻"), "游戏UI科幻HUD"),
    (("暗色", "dark"), "暗色友好"),
    (("渐变", "gradient"), "渐变高饱和"),
)
_STYLE_SUBJECTS = {
    "编辑风": {"editorial", "documentation", "site-inspiration"},
    "电商实感": {"commerce", "components"},
    "极简克制": {"design-system", "agent-guidance"},
    "玻璃拟态": {"visual-effects", "design-system"},
    "拟物质感": {"visual-effects", "components"},
    "游戏UI科幻HUD": {"game-ui"},
    "暗色友好": {"dashboard", "design-system"},
    "渐变高饱和": {"visual-effects"},
}


def aesthetic_fallback(brief_lower: str, patterns: list[dict], framework: str | None) -> list[tuple]:
    styles = [tag for words, tag in _AESTHETIC_HINTS if any(word in brief_lower for word in words)]
    if not styles:
        return []
    wanted = set().union(*(_STYLE_SUBJECTS.get(tag, set()) for tag in styles))
    ranked = []
    for pattern in patterns:
        frameworks = set(pattern["frameworks"])
        compatible = not framework or "agnostic" in frameworks or framework in frameworks or framework == "nextjs" and "react" in frameworks
        if not compatible:
            continue
        overlap = wanted & set(pattern["subjects"])
        if not overlap:
            continue
        ranked.append((3, pattern["id"], pattern, [f"风格:{styles[0]}", *sorted(overlap)]))
    return ranked


def get_pattern(data_root: Path, pattern_id: str, source_items: list[dict[str, Any]]) -> dict[str, Any]:
    pattern = load_patterns(data_root).get(pattern_id)
    if pattern is None:
        raise KeyError(pattern_id)
    return {
        **pattern,
        "source_credits": source_credits(pattern, source_items),
        "use_policy": USE_POLICY,
    }


def search_patterns(
    data_root: Path, brief: str, source_items: list[dict[str, Any]],
    *, framework: str | None = None, subject: str | None = None, limit: int = 5,
) -> list[dict[str, Any]]:
    brief_lower = brief.strip().lower()
    if len(brief_lower) < 2:
        raise ValueError("brief must have at least two characters")
    terms = {term for term in re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", brief_lower) if len(term) >= 2}
    terms = expand_query_terms(brief_lower, terms)
    ranked: list[tuple[int, str, dict[str, Any], list[str]]] = []
    for pattern in load_patterns(data_root).values():
        frameworks = set(pattern["frameworks"])
        compatible = not framework or "agnostic" in frameworks or framework in frameworks or framework == "nextjs" and "react" in frameworks
        if not compatible or subject and subject not in pattern["subjects"]:
            continue
        keyword_hits = [
            k for k in pattern["keywords"]
            if k.lower() in brief_lower or k.lower() in terms or any(term in k.lower() for term in terms)
        ]
        searchable = " ".join([pattern["id"], pattern["title"], pattern["summary"], *pattern["subjects"], *pattern["keywords"]]).lower()
        term_hits = [term for term in terms if term in searchable]
        text_score = len(keyword_hits) * 5 + len(term_hits) * 2
        if not text_score and not subject:
            continue
        score = text_score
        if subject and subject in pattern["subjects"]:
            score += 4
        if framework and framework in frameworks:
            score += 2
        if score:
            ranked.append((score, pattern["id"], pattern, sorted(set(keyword_hits + term_hits))))
    if not ranked and not subject:
        ranked = aesthetic_fallback(brief_lower, list(load_patterns(data_root).values()), framework)
    ranked.sort(key=lambda row: (-row[0], row[1]))
    results = []
    for score, _, pattern, hits in ranked[: max(1, min(limit, 20))]:
        row = {
            "id": pattern["id"], "title": pattern["title"], "summary": pattern["summary"],
            "subjects": pattern["subjects"], "frameworks": pattern["frameworks"],
            "match": hits[:8], "score": score,
            "source_credits": source_credits(pattern, source_items),
            "use_policy": USE_POLICY,
        }
        if any(str(hit).startswith("风格:") for hit in hits):
            row["fallback"] = "aesthetic"
        results.append(row)
    return results


def route_source(data_root: Path, item_id: str, source_items: list[dict[str, Any]]) -> dict[str, Any]:
    routes = load_routes(data_root)
    route = routes.get(item_id)
    if route is None:
        raise KeyError(item_id)
    if route["canonical_item_id"]:
        result = route_source(data_root, route["canonical_item_id"], source_items)
        return {"requested_item_id": item_id, "redirect_to": route["canonical_item_id"], "route": result}
    item = next(item for item in source_items if item["id"] == item_id)
    modes = [s.strip() for s in route["route_modes"].split(";") if s.strip()]
    return {
        "item_id": item_id, "title": item["title"], "knowledge_status": route["knowledge_status"],
        "pattern_ids": [s.strip() for s in route["pattern_ids"].split(";") if s.strip()],
        "route_modes": modes, "provider_status": route["provider_status"],
        "provider": {
            "transport": route["provider_transport"], "endpoint": route["provider_endpoint"],
            "requires": route["requires"], "cost": route["provider_tier"],
            "auth": item.get("provider_auth") or "none",
            "limit": item.get("provider_limit") or "none",
            "connection": "user-direct; Ailyre does not proxy or supply provider credentials",
        } if "provider-direct" in modes else None,
        "source": {"url": route["source_url"], "license": route["source_license"], "verified_at": route["verified_at"]},
        "instruction": "Use self patterns first. Connect to the provider only through the user's own account and current provider terms.",
    }
