FROM python:3.12

WORKDIR /app

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app/ app/

# Create data directories
RUN mkdir -p data/input data/output logs

# Install dependencies (pre-cache for faster startup)
RUN uv sync --no-dev

# Copy and setup entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Use entrypoint for startup tasks
ENTRYPOINT ["docker-entrypoint.sh"]
