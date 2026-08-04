# Base image pinned 2026-03-05 — refresh monthly or via Dependabot
FROM python:3.11-slim@sha256:d6e4d224f70f9e0172a06a3a2eba2f768eb146811a349278b38fff3a36463b47
WORKDIR /opt/pmoves-yt
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/opt/pmoves-yt
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg atomicparsley ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# JS runtime for YouTube player-response decoding. yt-dlp deprecated JS-less
# YouTube extraction (2026): without a runtime, format extraction fails even with
# valid cookies ("No supported JavaScript runtime could be found"). This image
# ships the JS-challenge machinery (yt_dlp/extractor/youtube/jsc) and registers
# DenoJCP, so the binary is required for the extractor to work at all.
#
# Placed BEFORE `COPY . /opt/pmoves-yt` so a fork-source change does not
# invalidate this ~40MB layer, and before `USER` since /usr/local/bin needs root.
# Fetched with python, NOT curl: this image has no curl (the healthcheck below
# uses python urllib), so a curl-based fetch fails the build.
# TARGETARCH-aware: this image is built linux/amd64,linux/arm64 — a hardcoded
# x86_64 binary cannot exec under arm64.
ARG TARGETARCH
ARG DENO_VERSION=v2.6.4
RUN set -eux; \
    case "${TARGETARCH:-amd64}" in \
      amd64) deno_arch=x86_64-unknown-linux-gnu ;; \
      arm64) deno_arch=aarch64-unknown-linux-gnu ;; \
      *) echo "unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    if [ "$DENO_VERSION" = "latest" ]; then \
      url="https://github.com/denoland/deno/releases/latest/download/deno-${deno_arch}.zip"; \
    else \
      url="https://github.com/denoland/deno/releases/download/${DENO_VERSION}/deno-${deno_arch}.zip"; \
    fi; \
    python -c "import urllib.request,sys; urllib.request.urlretrieve(sys.argv[1],'/tmp/deno.zip')" "$url"; \
    python -c "import zipfile,os; zipfile.ZipFile('/tmp/deno.zip').extractall('/usr/local/bin'); os.chmod('/usr/local/bin/deno',0o755)"; \
    rm /tmp/deno.zip; \
    deno --version
# deno defaults DENO_DIR to $HOME/.cache/deno, and HOME is /app for uid 65532.
# Set it explicitly rather than relying on passwd resolution; the dir is created
# below so the existing chown covers it.
ENV DENO_DIR=/app/.cache/deno

COPY . /opt/pmoves-yt
# Parameterize yt-dlp so operators can still override the packaged fork when needed.
ARG YTDLP_VERSION=
ARG YTDLP_PIP_URL=
RUN pip install --no-cache-dir --upgrade pip \
    "setuptools==82.0.0" "wheel==0.46.3" \
    && pip install --no-cache-dir -r pmoves_yt_service/requirements.lock \
    && if [ -n "$YTDLP_PIP_URL" ]; then pip install --no-cache-dir "$YTDLP_PIP_URL"; \
       elif [ -n "$YTDLP_VERSION" ]; then pip install --no-cache-dir "yt-dlp[default]==${YTDLP_VERSION}"; \
       else pip install --no-cache-dir ".[default]"; fi

# Security: Run as non-root user
RUN groupadd -r pmoves --gid=65532 && \
    useradd -r -g pmoves --uid=65532 --home-dir=/app --shell=/sbin/nologin pmoves && \
    mkdir -p /app/config /app/.cache/deno /data/yt-dlp && \
    chown -R pmoves:pmoves /app /opt/pmoves-yt /data

USER pmoves:pmoves
WORKDIR /app

EXPOSE 8077
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8077/healthz', timeout=4).read()" || exit 1
CMD ["uvicorn","pmoves_yt_service.yt:app","--host","0.0.0.0","--port","8077"]
