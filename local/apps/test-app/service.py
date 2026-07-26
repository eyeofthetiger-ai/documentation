#!/usr/bin/env python3
"""test-app: a minimal app for exercising the on-device apps platform's
integration with continuous recording and events -- no camera/CV work at
all, just timed calls into the capture server's own local API.

Every CYCLE_S (60s): start continuous recording, wait RECORD_S (10s), stop
continuous recording, then POST a "declared" event, then idle for whatever's
left of the cycle before repeating.

The event is declared *after* stopping, not before: services/library.py's
stop() blocks until the just-finished segment is fully muxed and written to
the durable index (see _close_segment), so by the time stop() returns, the
segment is already closed and indexed -- find_segment_at can match the
event against it, giving every event a real `recording_id`/`offset_s`
instead of `null`.

Run:
    python service.py --capture-url http://127.0.0.1:80 --port 8101
"""

from __future__ import annotations

import argparse
import threading
import time
from datetime import datetime, timezone

import requests
import uvicorn
from fastapi import FastAPI

CYCLE_S = 60
RECORD_S = 10
EVENT_TYPE = "test-app.tick"

# Continuous recording's own start()/stop() 409 if it's already in the
# state being requested (e.g. start while already recording) -- tolerated
# here rather than treated as a real error, since another cycle or an
# unrelated caller toggling continuous recording shouldn't spam this app's
# own last_error with something that isn't actually broken.
_TOLERATED_STATUS = {200, 409}


class State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.cycle = 0
        self.phase = "starting up"
        self.last_cycle_started_at: str | None = None
        self.last_event_at: str | None = None
        self.last_error: str | None = None


STATE = State()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(message: str) -> None:
    print(f"[test-app] {_now_iso()} {message}", flush=True)


def _post(capture_url: str, path: str, **kwargs) -> requests.Response:
    return requests.post(f"{capture_url.rstrip('/')}{path}", timeout=10, **kwargs)


def _set_phase(phase: str) -> None:
    with STATE.lock:
        STATE.phase = phase
    _log(phase)


def _record_error(context: str, error: Exception) -> None:
    message = f"{context}: {type(error).__name__}: {error}"
    with STATE.lock:
        STATE.last_error = message
    _log(f"error: {message}")


def run_cycle(capture_url: str) -> None:
    with STATE.lock:
        STATE.last_cycle_started_at = _now_iso()
    _set_phase("starting continuous recording")
    try:
        response = _post(capture_url, "/continuous-recording/start")
        if response.status_code not in _TOLERATED_STATUS:
            response.raise_for_status()
    except Exception as error:  # noqa: BLE001
        _record_error("start failed", error)

    # Taken right after start()'s response, not before the request -- the
    # segment's own started_at is stamped server-side while handling that
    # request, so a timestamp captured before sending it could land earlier
    # than the segment's started_at and miss find_segment_at's match.
    # RECORD_S of sleep still ahead gives it comfortable margin before the
    # segment's ended_at too.
    event_at = _now_iso()

    time.sleep(RECORD_S)

    _set_phase("stopping continuous recording")
    try:
        response = _post(capture_url, "/continuous-recording/stop")
        if response.status_code not in _TOLERATED_STATUS:
            response.raise_for_status()
    except Exception as error:  # noqa: BLE001
        _record_error("stop failed", error)

    # Declared only now, after stop() has returned -- stop() blocks until
    # the segment is closed and written to the durable index (see
    # services/library.py _close_segment), so the segment covering event_at
    # is guaranteed to already be indexed by the time this POSTs.
    _set_phase("declaring event")
    with STATE.lock:
        STATE.last_event_at = event_at
        cycle = STATE.cycle
    try:
        response = _post(
            capture_url,
            "/events",
            json={
                "type": EVENT_TYPE,
                "started_at": event_at,
                "ended_at": event_at,
                "payload": {"cycle": cycle},
            },
        )
        response.raise_for_status()
    except Exception as error:  # noqa: BLE001
        _record_error("event POST failed", error)

    with STATE.lock:
        STATE.cycle += 1
    _set_phase("idle")


def timer_loop(capture_url: str) -> None:
    while True:
        cycle_start = time.monotonic()
        run_cycle(capture_url)
        elapsed = time.monotonic() - cycle_start
        time.sleep(max(0.0, CYCLE_S - elapsed))


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
api = FastAPI(title="test-app", version="0.1.0")


@api.get("/status")
def status():
    with STATE.lock:
        return {
            "cycle": STATE.cycle,
            "phase": STATE.phase,
            "last_cycle_started_at": STATE.last_cycle_started_at,
            "last_event_at": STATE.last_event_at,
            "last_error": STATE.last_error,
        }


@api.get("/healthz")
def healthz():
    return {"status": "ok"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--capture-url",
        default="http://127.0.0.1:80",
        help="Capture server's base URL, for continuous-recording start/stop and POST /events.",
    )
    parser.add_argument("--port", type=int, default=8101)
    args = parser.parse_args()

    threading.Thread(target=timer_loop, args=(args.capture_url,), daemon=True).start()
    print(f"test-app: http://0.0.0.0:{args.port}  (capture server: {args.capture_url})")
    uvicorn.run(api, host="0.0.0.0", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
