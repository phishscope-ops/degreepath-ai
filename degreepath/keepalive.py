"""Keep the free Render instance warm.

Render's free web services sleep after ~15 minutes without inbound traffic.
When deployed (RENDER_EXTERNAL_URL is set by Render, or SELF_URL is given),
a daemon thread pings our own /health every 10 minutes so the service stays
awake. /health does not touch the database, so the Neon compute can still
scale to zero and does not burn its free compute-hours.

Disable with KEEPALIVE_SELF_PING=0.
"""
import os
import threading
import time

import requests

_INTERVAL = 600  # seconds, under Render's 15-minute idle window


def maybe_start(app):
    if app.config.get("TESTING"):
        return
    if os.environ.get("KEEPALIVE_SELF_PING", "1").lower() in ("0", "false", "no"):
        return
    base = os.environ.get("SELF_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    if not base:
        return
    url = base.rstrip("/") + "/health"

    def loop():
        time.sleep(120)  # let the deploy settle before the first ping
        while True:
            try:
                requests.get(url, timeout=15)
            except Exception:
                pass
            time.sleep(_INTERVAL)

    threading.Thread(target=loop, daemon=True).start()
