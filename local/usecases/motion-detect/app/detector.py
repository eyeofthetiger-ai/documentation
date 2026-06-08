#!/usr/bin/env python3
"""Motion detection event recorder for an MJPEG stream."""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from collections import deque
from datetime import datetime

import cv2
import numpy as np

STREAM_URL = "http://eyeofthetiger.local/stream.mjpg"
EVENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "events")

# Downscale factor applied before comparison (speeds up processing, reduces noise)
SCALE = 0.5

running = True


def handle_sigint(sig, frame):
    global running
    print("\n[detector] Ctrl-C received — shutting down.")
    running = False


def open_stream(url: str) -> cv2.VideoCapture:
    print(f"[detector] Connecting to {url} …")
    cap = cv2.VideoCapture(url)
    if cap.isOpened():
        print("[detector] Stream open.")
    else:
        print("[detector] Could not open stream.")
    return cap


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
    # Amplify diff for easy human viewing
    diff_vis = cv2.applyColorMap(cv2.convertScaleAbs(diff, alpha=3), cv2.COLORMAP_HOT)
    return score, diff_vis


def save_event(event_dir: str, initial: np.ndarray, second: np.ndarray,
               diff_vis: np.ndarray, score: float, args: argparse.Namespace) -> None:
    os.makedirs(event_dir, exist_ok=True)
    cv2.imwrite(os.path.join(event_dir, "initial.jpg"), initial)
    cv2.imwrite(os.path.join(event_dir, "second.jpg"), second)
    cv2.imwrite(os.path.join(event_dir, "diff.jpg"), diff_vis)

    meta = {
        "timestamp": os.path.basename(event_dir),
        "score": round(score, 6),
        "pixel_threshold": args.pixel_threshold,
        "changed_area_threshold": args.changed_area_threshold,
        "frame_gap": args.frame_gap,
        "record_seconds": args.record_seconds,
        "files": ["initial.jpg", "second.jpg", "diff.jpg", "event.mp4"],
    }
    with open(os.path.join(event_dir, "event.json"), "w") as f:
        json.dump(meta, f, indent=2)


def record_clip(cap: cv2.VideoCapture, event_dir: str, seconds: float,
                fps_estimate: float) -> None:
    """Record frames for `seconds` and write a raw AVI, then convert to H.264 MP4."""
    raw_path = os.path.join(event_dir, "_raw.avi")
    mp4_path = os.path.join(event_dir, "event.mp4")

    ret, first_frame = cap.read()
    if not ret:
        print("[detector] Could not read first clip frame.")
        return

    h, w = first_frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    out = cv2.VideoWriter(raw_path, fourcc, fps_estimate, (w, h))
    out.write(first_frame)

    deadline = time.monotonic() + seconds
    frames_written = 1
    while time.monotonic() < deadline:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        frames_written += 1

    out.release()
    print(f"[detector] Recorded {frames_written} frames → converting to MP4 …")

    result = subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", raw_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-movflags", "+faststart",
            mp4_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[detector] ffmpeg error: {result.stderr.strip()}")
    else:
        os.remove(raw_path)
        print(f"[detector] Saved {mp4_path}")


def estimate_fps(cap: cv2.VideoCapture, sample_frames: int = 10) -> float:
    """Read a few frames to estimate actual stream FPS."""
    t0 = time.monotonic()
    for _ in range(sample_frames):
        cap.read()
    elapsed = time.monotonic() - t0
    fps = sample_frames / elapsed if elapsed > 0 else 10.0
    print(f"[detector] Estimated stream FPS: {fps:.1f}")
    return fps


def main() -> None:
    parser = argparse.ArgumentParser(description="MJPEG motion detector")
    parser.add_argument("--frame-gap", type=int, default=5,
                        help="Compare frames this many frames apart (default: 5)")
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
    os.makedirs(EVENTS_DIR, exist_ok=True)

    print(f"[detector] Settings: frame-gap={args.frame_gap}, "
          f"record-seconds={args.record_seconds}, "
          f"pixel-threshold={args.pixel_threshold}, "
          f"changed-area-threshold={args.changed_area_threshold}, "
          f"cooldown={args.cooldown}s")

    while running:
        cap = open_stream(STREAM_URL)

        if not cap.isOpened():
            print("[detector] Retrying in 5 s …")
            time.sleep(5)
            continue

        fps = estimate_fps(cap)
        # Ring buffer to hold the last `frame_gap` raw frames for comparison
        raw_buffer: deque = deque(maxlen=args.frame_gap)
        # Matching buffer of preprocessed frames
        pre_buffer: deque = deque(maxlen=args.frame_gap)

        last_event_time = 0.0
        print("[detector] Monitoring …")

        while running:
            ret, frame = cap.read()
            if not ret:
                print("[detector] Stream lost — reconnecting …")
                break

            pre = preprocess(frame)
            raw_buffer.append(frame)
            pre_buffer.append(pre)

            # Need a full buffer before we can compare
            if len(pre_buffer) < args.frame_gap:
                continue

            in_cooldown = (time.monotonic() - last_event_time) < args.cooldown
            if in_cooldown:
                continue

            older_pre = pre_buffer[0]
            score, diff_vis = motion_score(older_pre, pre, args.pixel_threshold)

            if score >= args.changed_area_threshold:
                ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                event_dir = os.path.join(EVENTS_DIR, ts)
                print(f"[detector] Motion detected! score={score:.4f} → saving event {ts}")

                # Upscale diff_vis back to full resolution for clarity
                h, w = raw_buffer[0].shape[:2]
                diff_full = cv2.resize(diff_vis, (w, h), interpolation=cv2.INTER_NEAREST)

                save_event(event_dir, raw_buffer[0], frame, diff_full, score, args)
                print(f"[detector] Saved initial.jpg, second.jpg, diff.jpg, event.json → {event_dir}")

                record_clip(cap, event_dir, args.record_seconds, fps)

                last_event_time = time.monotonic()
                raw_buffer.clear()
                pre_buffer.clear()
                print("[detector] Monitoring …")

        cap.release()
        if running:
            time.sleep(3)

    print("[detector] Done.")


if __name__ == "__main__":
    main()
