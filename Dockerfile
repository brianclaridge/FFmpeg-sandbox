FROM python:3.12

# Build args for version info (computed at build time)
ARG GIT_HASH=dev
ARG GIT_DATE=

# Set as environment variables
ENV GIT_HASH=${GIT_HASH}
ENV GIT_DATE=${GIT_DATE}

WORKDIR /app

# Install ffmpeg and curl (for health checks)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app/ app/

# Create data directories
RUN mkdir -p .data/input .data/output .data/logs

# Install dependencies (pre-cache for faster startup)
RUN uv sync --no-dev

# Copy and setup entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Use entrypoint for startup tasks
ENTRYPOINT ["docker-entrypoint.sh"]
