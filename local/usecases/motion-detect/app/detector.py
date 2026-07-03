#!/usr/bin/env python3
"""Motion detection event recorder using still-image polling."""

import argparse
import json
import os
import signal
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import requests

IMAGE_URL = "http://eyeofthetiger.local/v1/snapshot"
CLIP_URL = "http://eyeofthetiger.local/v1/clip"
EVENTS_DIR = Path(__file__).parent.parent / "output" / "events"

SCALE = 0.5

running = True


def handle_sigint(sig, frame):
    global running
    print("\n[detector] Ctrl-C received — shutting down.")
    running = False


def fetch_frame() -> np.ndarray | None:
    """Fetch one JPEG from the device and decode it as a BGR frame."""
    try:
        resp = requests.get(IMAGE_URL, timeout=10)
        if resp.status_code != 200:
            print(f"[detector] Image fetch returned {resp.status_code}")
            return None
        arr = np.frombuffer(resp.content, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except requests.RequestException as exc:
        print(f"[detector] Image fetch failed: {exc}")
        return None


def preprocess(frame: np.ndarray) -> np.ndarray:
    """Downscale, convert to greyscale, and blur a frame for comparison."""
    small = cv2.resize(frame, (0, 0), fx=SCALE, fy=SCALE)
    grey = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(grey, (21, 21), 0)


def motion_score(a: np.ndarray, b: np.ndarray, pixel_threshold: int) -> tuple[float, np.ndarray]:
    """Return (changed_proportion, diff_image) between two preprocessed frames."""
    diff = cv2.absdiff(a, b)
    _, mask = cv2.threshold(diff, pixel_threshold, 255, cv2.THRESH_BINARY)
    score = np.count_nonzero(mask) / mask.size
    diff_vis = cv2.applyColorMap(cv2.convertScaleAbs(diff, alpha=3), cv2.COLORMAP_HOT)
    return score, diff_vis


def record_event_clip(event_dir: Path, seconds: float) -> bool:
    """Request a fixed-length clip from the device and download the MP4."""
    print(f"[detector] Recording {seconds}s clip …")
    try:
        resp = requests.get(CLIP_URL, params={"duration_s": int(seconds)}, timeout=seconds + 30)
        if resp.status_code != 200:
            print(f"[detector] Record clip failed: {resp.status_code} {resp.text}")
            return False
        mp4_path = event_dir / "event.mp4"
        mp4_path.write_bytes(resp.content)
        print(f"[detector] Saved {mp4_path} ({len(resp.content)} bytes)")
        return True
    except requests.RequestException as exc:
        print(f"[detector] Failed to record clip: {exc}")
        return False


def save_event(event_dir: Path, initial: np.ndarray, second: np.ndarray,
               diff_vis: np.ndarray, score: float, args: argparse.Namespace) -> None:
    event_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(event_dir / "initial.jpg"), initial)
    cv2.imwrite(str(event_dir / "second.jpg"), second)

    h, w = initial.shape[:2]
    diff_full = cv2.resize(diff_vis, (w, h), interpolation=cv2.INTER_NEAREST)
    cv2.imwrite(str(event_dir / "diff.jpg"), diff_full)

    meta = {
        "timestamp": event_dir.name,
        "score": round(score, 6),
        "pixel_threshold": args.pixel_threshold,
        "changed_area_threshold": args.changed_area_threshold,
        "poll_interval_s": args.poll_interval,
        "record_seconds": args.record_seconds,
        "files": ["initial.jpg", "second.jpg", "diff.jpg", "event.mp4"],
    }
    with open(event_dir / "event.json", "w") as f:
        json.dump(meta, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Still-image motion detector")
    parser.add_argument("--poll-interval", type=float, default=1.0,
                        help="Seconds between image fetches (default: 1.0)")
    parser.add_argument("--record-seconds", type=float, default=10.0,
                        help="Seconds of video to record after motion (default: 10)")
    parser.add_argument("--pixel-threshold", type=int, default=25,
                        help="Per-pixel diff value that counts as changed (default: 25)")
    parser.add_argument("--changed-area-threshold", type=float, default=0.02,
                        help="Proportion of changed pixels that triggers an event (default: 0.02)")
    parser.add_argument("--cooldown", type=float, default=15.0,
                        help="Seconds to ignore motion after an event (default: 15)")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, handle_sigint)
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[detector] Settings: poll-interval={args.poll_interval}s, "
          f"record-seconds={args.record_seconds}, "
          f"pixel-threshold={args.pixel_threshold}, "
          f"changed-area-threshold={args.changed_area_threshold}, "
          f"cooldown={args.cooldown}s")

    prev_frame: np.ndarray | None = None
    prev_pre: np.ndarray | None = None
    last_event_time = 0.0

    print("[detector] Monitoring …")

    while running:
        frame = fetch_frame()
        if frame is None:
            print("[detector] Retrying in 5 s …")
            time.sleep(5)
            continue

        pre = preprocess(frame)

        if prev_pre is None:
            prev_frame, prev_pre = frame, pre
            time.sleep(args.poll_interval)
            continue

        in_cooldown = (time.monotonic() - last_event_time) < args.cooldown
        if not in_cooldown:
            score, diff_vis = motion_score(prev_pre, pre, args.pixel_threshold)

            if score >= args.changed_area_threshold:
                ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                event_dir = EVENTS_DIR / ts
                print(f"[detector] Motion detected! score={score:.4f} → saving event {ts}")
                save_event(event_dir, prev_frame, frame, diff_vis, score, args)
                print(f"[detector] Saved initial.jpg, second.jpg, diff.jpg, event.json → {event_dir}")
                record_event_clip(event_dir, args.record_seconds)
                last_event_time = time.monotonic()
                prev_frame, prev_pre = None, None
                print("[detector] Monitoring …")
                time.sleep(args.poll_interval)
                continue

        prev_frame, prev_pre = frame, pre
        time.sleep(args.poll_interval)

    print("[detector] Done.")


if __name__ == "__main__":
    main()
