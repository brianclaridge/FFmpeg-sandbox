#!/usr/bin/env python3
"""Wait for Docker container health check, then open browser."""

import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from urllib.request import urlopen

URL = "http://localhost:8000"
HEALTH_URL = f"{URL}/health"
MAX_WAIT = 60  # seconds
POLL_INTERVAL = 1  # seconds


def check_health() -> bool:
    """Check if the health endpoint responds."""
    try:
        with urlopen(HEALTH_URL, timeout=2) as response:
            return response.status == 200
    except Exception:
        # Catch all exceptions - container may not be ready yet
        return False


def get_git_hash() -> str:
    """Get current git commit short hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "dev"


def main() -> int:
    print(f"Waiting for {HEALTH_URL} to become healthy...")

    elapsed = 0
    while elapsed < MAX_WAIT:
        if check_health():
            print(f"Container healthy after {elapsed}s")
            # Build cache-busting URL: ?_={YYYYMMDD}_{timestamp}&commit={sha}
            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            timestamp = int(now.timestamp())
            commit = get_git_hash()
            cache_bust_url = f"{URL}?_={date_str}_{timestamp}&commit={commit}"
            print(f"Opening {cache_bust_url}")
            webbrowser.open(cache_bust_url)
            return 0

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        if elapsed % 5 == 0:
            print(f"  Still waiting... ({elapsed}s)")

    print(f"Timeout: Container not healthy after {MAX_WAIT}s")
    return 1


if __name__ == "__main__":
    sys.exit(main())
