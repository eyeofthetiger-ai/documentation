"""hello-cloud-app: the smallest cloud app you can submit to the EyeOfTheTiger
app library.

Once a minute it asks the platform about the EOT-1 it was installed for, and
it reports the last answer on GET /status. Standard library only, so the
Dockerfile needs no requirements file.
"""
import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Set by the platform on every cloud app it runs.
API_URL = os.environ["CAMERA_API_URL"].rstrip("/")
API_KEY = os.environ["CAMERA_API_KEY"]
CAMERA_ID = os.environ["CAMERA_ID"]
# Set by Cloud Run to the port you entered when you submitted the app.
PORT = int(os.environ.get("PORT", "8080"))

last_check = {"checked_at": None, "camera_reachable": None, "error": None}


def poll_forever():
    url = f"{API_URL}/api/v1/cameras/{CAMERA_ID}/status"
    while True:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"x-api-key": API_KEY}), timeout=10):
                last_check.update(camera_reachable=True, error=None)
        except (urllib.error.URLError, OSError) as e:
            last_check.update(camera_reachable=False, error=str(e))
        last_check["checked_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        time.sleep(60)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_error(404)
            return
        body = json.dumps(last_check).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    threading.Thread(target=poll_forever, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
