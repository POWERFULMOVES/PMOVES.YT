# PMOVES.YT Runtime

PMOVES.YT is the authoritative PMOVES YouTube ingest runtime and the upstream yt-dlp fork consumed by PMOVES.AI.

Canonical runtime files:
- `pmoves_yt_service/yt.py`
- `pmoves_yt_service/docs_sync.py`
- `pmoves_yt_service/docs_catalog.py`
- `pmoves_yt_service/Dockerfile`

Runtime model:
- PMOVES.AI consumes this repo as a submodule and builds `pmoves-yt` from here.
- `pmoves/services/pmoves-yt` in the root repo is a compatibility mirror only.
- `/yt/docs/catalog` and `/yt/docs/sync` are owned here.

Local build:
```bash
docker build -f pmoves_yt_service/Dockerfile -t pmoves-yt:dev .
```

Local run:
```bash
docker run --rm -p 8077:8077 pmoves-yt:dev
```

Primary validation:
```bash
curl http://localhost:8077/healthz
curl http://localhost:8077/yt/docs/catalog
python -m pytest -q pmoves_yt_service/tests
```
