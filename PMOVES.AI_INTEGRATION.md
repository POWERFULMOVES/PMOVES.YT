# PMOVES.AI Integration Guide for PMOVES YT

## Integration Complete

The PMOVES.AI integration template has been applied to PMOVES YT.

## Environment Files

This integration provides environment files for both shell sourcing and Docker Compose:

### Shell Usage (for development/testing)
Source the `.sh` versions directly in your shell:
```bash
source env.shared.sh
source env.tier-worker.sh
```

### Docker Compose Usage
Use the non-`.sh` versions with `env_file` directive:
```yaml
services:
  pmoves-yt:
    env_file:
      - env.shared
```

## Next Steps

### 1. Customize Environment Variables

Edit the following files with your service-specific values:

- `env.shared` / `env.shared.sh` - Base environment configuration
- `env.tier-worker` / `env.tier-worker.sh` - Tier-specific environment

Note: Both formats are provided for flexibility. The `.sh` files use `export` for shell sourcing, while non-`.sh` files use plain `KEY=value` for Docker Compose.

**Important:** Set actual credentials before running in production. Default values are intentionally empty to fail fast.

### 2. Update Docker Compose

Add the PMOVES.AI environment anchor to your `docker-compose.yml`:

```yaml
services:
  pmoves-yt:
    <<: [*env-tier-worker, *pmoves-healthcheck, *pmoves-labels]
    image: ghcr.io/powerfulmoves/pmoves-yt:latest
    ports:
      - "8077:8077"
    environment:
      SERVICE_NAME: pmoves-yt
      SERVICE_PORT: 8077
      METRICS_PORT: 9180
```

**Important:** Use the array merge form `<<: [*anchor1, *anchor2, ...]` not separate `<<:` directives.

### 3. Integrate Health Check

Add the health check endpoint to your service:

```python
from pmoves_health import add_custom_check, get_health_status

@app.get("/healthz")
async def health_check():
    return await get_health_status()
```

### 4. Add Service Announcement

Add NATS service announcement to your startup using the lifespan pattern:

```python
from contextlib import asynccontextmanager
from pmoves_announcer import announce_service

@asynccontextmanager
async def lifespan(app):
    # Startup
    await announce_service(
        slug="pmoves-yt",
        name="PMOVES YT",
        url="http://pmoves-yt:8077",
        port=8077,
        tier="worker"
    )
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)
```

Note: The `@app.on_event("startup")` decorator is deprecated in FastAPI. Use the `lifespan` context manager instead.

### 5. Test Integration

```bash
# Test health check
curl http://localhost:8077/healthz

# Verify environment variables loaded
docker compose exec pmoves-yt env | grep PMOVES

# Verify NATS announcement
nats sub "services.announce.v1"
```

## Service Details

- **Name:** PMOVES YT
- **Slug:** pmoves-yt
- **Tier:** worker
- **Port:** 8077
- **Health Check:** http://localhost:8077/healthz
- **Metrics:** http://localhost:9180/metrics
- **NATS Enabled:** True
- **GPU Enabled:** False

## Files Created

- `env.shared` / `env.shared.sh` - Base PMOVES.AI environment
- `env.tier-worker` / `env.tier-worker.sh` - Tier-specific environment
- `chit/secrets_manifest_v2.yaml` - CHIT secrets configuration
- `pmoves_health/` - Health check module
- `pmoves_announcer/` - NATS service announcer
- `pmoves_registry/` - Service registry client
- `docker-compose.pmoves.yml` - PMOVES.AI YAML anchors

## Docker Compose Notes

1. **YAML Merge Syntax**: Use `<<: [*anchor1, *anchor2]` for multiple anchors. Do not use separate `<<:` directives as this violates YAML spec.

2. **Environment Format**: Use mapping syntax (`KEY: value`) not array syntax (`- KEY=value`) for better readability.

3. **Health Check Ports**: The `${SERVICE_PORT:-8080}` in healthcheck is interpolated from the host environment or `.env` file, NOT from the service's `environment` block. Set it in your `.env` file before running docker compose, or override `healthcheck.test` explicitly per service.

4. **Prometheus Labels**: Labels use slash separator (`prometheus.io/port`) not dot (`prometheus.io.port`).

## Support

For questions or issues, see the PMOVES.AI documentation.
