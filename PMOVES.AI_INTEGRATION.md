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

- `env.shared` - Base environment configuration (Docker Compose format)
- `env.shared.sh` - Base environment configuration (shell format with `export`)
- `env.tier-worker` - Worker tier configuration (Docker Compose format)
- `env.tier-worker.sh` - Worker tier configuration (shell format)

Note: Both formats are provided for flexibility. The `.sh` files use `export` for shell sourcing, while non-`.sh` files use plain `KEY=value` for Docker Compose.

### 2. Update Docker Compose

Add the PMOVES.AI environment anchor to your `docker-compose.yml`:

```yaml
services:
  pmoves-yt:
    <<: *env-tier-worker
    <<: *pmoves-healthcheck
    <<: *pmoves-labels
    image: ghcr.io/powerfulmoves/pmoves-yt:latest
    ports:
      - "8077:8077"
    environment:
      SERVICE_NAME: pmoves-yt
      SERVICE_PORT: 8077
      METRICS_PORT: 9077
```

Important: Use separate `<<:` merge directives for each anchor (not array syntax).

### 3. Integrate Health Check

Add the health check endpoint to your service:

```python
from pmoves_health import add_custom_check, get_health_status

@app.get("/healthz")
async def health_check():
    return await get_health_status()
```

### 4. Add Service Announcement

Add NATS service announcement to your startup:

```python
from pmoves_announcer import announce_service

@app.on_event("startup")
async def startup():
    await announce_service(
        slug="pmoves-yt",
        name="PMOVES YT",
        url="http://pmoves-yt:8077",
        port=8077,
        tier="worker"
    )
```

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
- **Metrics:** http://localhost:9077/metrics
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

1. **YAML Merge Behavior**: The `<<:` anchor merge replaces lists entirely. Each tier anchor includes all base environment variables explicitly to avoid losing NATS_URL, TENSORZERO_URL, etc.

2. **Environment Format**: Use mapping syntax (`KEY: value`) not array syntax (`- KEY=value`) for better readability and variable substitution.

3. **Multiple Anchors**: When using multiple anchors, use separate `<<:` directives (not `<<: [*anchor1, *anchor2]`).

4. **Configurable Ports**: Health check uses `${SERVICE_PORT:-8080}` for port flexibility. Set `SERVICE_PORT` or `METRICS_PORT` in your service environment.

## Support

For questions or issues, see the PMOVES.AI documentation.
