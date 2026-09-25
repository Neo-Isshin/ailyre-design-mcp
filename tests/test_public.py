import csv
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))
import app  # noqa: E402
import knowledge_api  # noqa: E402


def test_public_source_mirror_is_text_only_and_complete():
    with (ROOT / "index.csv").open(newline="", encoding="utf-8") as f:
        sources = list(csv.DictReader(f))
    assert knowledge_api.validate_repository(ROOT, sources, check_evidence=False) == {"patterns": 19, "sources": 190}
    assert app.open_source_manifest() == {}
    assert not (ROOT / "archive").exists()
    assert not (ROOT / "metadata").exists()


def test_mcp_pattern_route_without_private_archive():
    previous = os.environ.get("SITE_COLLECTION_DATA")
    os.environ["SITE_COLLECTION_DATA"] = str(ROOT)
    app._load_items_cached.cache_clear()
    try:
        with TestClient(app.app) as client:
            response = client.get("/v1/design-route", params={"brief": "SaaS dashboard", "framework": "react"})
            assert response.status_code == 200
            assert response.json()["self_patterns"]
            pattern = client.get("/v1/patterns/dashboard-app-shell")
            assert pattern.status_code == 200
            assert pattern.json()["source_credits"]
    finally:
        app._load_items_cached.cache_clear()
        if previous is None:
            os.environ.pop("SITE_COLLECTION_DATA", None)
        else:
            os.environ["SITE_COLLECTION_DATA"] = previous
