from fastapi.testclient import TestClient

from pmoves_yt_service import yt as app_module
from pmoves_yt_service.docs_sync import collect_yt_dlp_docs


def test_docs_catalog_endpoint_smoke():
    client = TestClient(app_module.app)
    resp = client.get("/yt/docs/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("ok") is True
    assert data["meta"]["yt_dlp_version"] != "unknown"
    assert data["meta"]["extractor_count"] > 0
    assert data["counts"]["options"] > 0


def test_docs_sync_collects_real_version():
    data = collect_yt_dlp_docs()
    assert data["version"] != "unknown"
