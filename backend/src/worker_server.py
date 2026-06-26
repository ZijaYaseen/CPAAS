"""Cloud Run wrapper: starts Celery worker + minimal HTTP health-check server.

Cloud Run requires a container to listen on a port. This script runs a tiny
health-check HTTP server on PORT (default 8080) in a background thread while
the Celery worker runs in the foreground.
"""

import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok","service":"worker"}')

    def log_message(self, format, *args):  # silence access logs
        pass


def _run_health_server(port: int) -> None:
    HTTPServer(("0.0.0.0", port), _HealthHandler).serve_forever()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    t = threading.Thread(target=_run_health_server, args=(port,), daemon=True)
    t.start()

    result = subprocess.run(
        [
            "uv", "run", "celery",
            "-A", "src.celery_app.celery_app",
            "worker",
            "--loglevel=info",
            "--queues=default,messages,webhooks,ai,email",
        ]
    )
    sys.exit(result.returncode)
