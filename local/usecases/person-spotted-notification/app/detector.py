#!/usr/bin/env python3
"""Person-detection notifier: monitors an MJPEG stream for motion, then uses
Ollama to classify whether a person is present and posts to Slack."""

import argparse
import base64
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import requests

from slack_poster import check_slack_env, send_slack_alert

STREAM_URL = "http://eyeofthetiger.local/v1/stream.mjpg"
OLLAMA_BASE_URL = "http://localhost:11434"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "events"

PERSON_PROMPT = (
    "Look at this image and determine whether there is a person visible. "
    "Respond with valid JSON only, no other text. The JSON must have a single "
    'boolean field: {"person": true} if a person is visible, or '
    '{"person": false} if not.'
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

running = True


def handle_sigint(sig, frame):
    global running
    log.info("Shutting down...")
    running = False


signal.signal(signal.SIGINT, handle_sigint)


def parse_args():
    p = argparse.ArgumentParser(description="Motion-triggered person detector")
    p.add_argument("--frame-gap", type=int, default=5,
                   help="Number of frames between the two comparison frames (default: 5)")
    p.add_argument("--pixel-threshold", type=int, default=25,
                   help="Per-pixel difference threshold 0-255 (default: 25)")
    p.add_argument("--area-threshold", type=float, default=0.02,
                   help="Fraction of changed pixels that triggers a check (default: 0.02)")
    p.add_argument("--cooldown", type=float, default=10.0,
                   help="Seconds to wait after AI returns before triggering again (default: 10)")
    p.add_argument("--model", default="gemma4",
                   help="Ollama vision model to use (default: gemma4)")
    p.add_argument("--reconnect-delay", type=float, default=3.0,
                   help="Seconds to wait before reconnecting after stream loss (default: 3)")
    p.add_argument("--video-duration", type=float, default=10.0,
                   help="Seconds of video to capture and post when a person is confirmed (default: 10)")
    return p.parse_args()


def preprocess(frame):
    """Downscale, convert to grayscale, and blur for stable diffing."""
    small = cv2.resize(frame, (320, 240))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (21, 21), 0)


def motion_score(frame_a, frame_b, pixel_threshold):
    """Return proportion of pixels that differ by more than pixel_threshold."""
    diff = cv2.absdiff(frame_a, frame_b)
    changed = np.sum(diff > pixel_threshold)
    return changed / diff.size


def classify_person(image_path: Path, model: str) -> tuple[bool, str]:
    """Send image to Ollama; return (person_bool, raw_response_string)."""
    with open(image_path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()

    payload = {
        "model": model,
        "prompt": PERSON_PROMPT,
        "images": [b64],
        "stream": False,
        "format": "json",
    }
    log.info("Calling Ollama model '%s' on %s …", model, image_path.name)
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "")
    except requests.RequestException as exc:
        error_msg = f"Ollama request failed: {exc}"
        log.warning(error_msg)
        return False, error_msg

    try:
        data = json.loads(raw)
        person = bool(data.get("person", False))
    except (json.JSONDecodeError, AttributeError):
        log.warning("Could not parse Ollama response as JSON: %r — treating as no person", raw)
        person = False

    return person, raw


def capture_video(event_dir: Path, duration: float) -> Path | None:
    """Open the video stream, record for duration seconds, save as MP4; return path or None."""
    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        log.warning("Could not open video stream: %s", STREAM_URL)
        return None

    ret, first_frame = cap.read()
    if not ret:
        cap.release()
        log.warning("Could not read first frame from video stream")
        return None

    frames = [first_frame]
    log.info("Capturing %.1fs of video …", duration)
    start = time.time()
    while time.time() - start < duration:
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    elapsed = time.time() - start
    cap.release()

    fps = len(frames) / elapsed
    h, w = frames[0].shape[:2]
    video_path = event_dir / "event.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, fps, (w, h))
    for f in frames:
        writer.write(f)
    writer.release()

    log.info("Saved %d-frame video at %.1f fps to %s", len(frames), fps, video_path.name)
    return video_path


def save_event(event_dir: Path, timestamp: str, model: str, score: float,
               args, raw_response: str, person: bool, video_path: Path | None,
               error: str | None = None, slack_posted: bool = False):
    event = {
        "timestamp": timestamp,
        "model": model,
        "motion_score": round(score, 6),
        "thresholds": {
            "pixel": args.pixel_threshold,
            "area": args.area_threshold,
        },
        "frame_gap": args.frame_gap,
        "cooldown_seconds": args.cooldown,
        "images": {
            "initial": "initial.jpg",
            "second": "second.jpg",
        },
        "video": video_path.name if video_path else None,
        "raw_model_response": raw_response,
        "person": person,
        "slack_posted": slack_posted,
    }
    if error:
        event["error"] = error
    path = event_dir / "event.json"
    path.write_text(json.dumps(event, indent=2))
    return path


def open_stream(url: str):
    log.info("Connecting to stream: %s", url)
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        return None
    log.info("Stream connected.")
    return cap


def run(args):
    global running
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cap = None
    frame_buffer = []   # ring of (processed, raw) tuples, length = frame_gap + 1
    cooldown_until = 0.0

    while running:
        # --- ensure stream is open ---
        if cap is None or not cap.isOpened():
            cap = open_stream(STREAM_URL)
            if cap is None:
                log.warning("Could not open stream, retrying in %.1fs …", args.reconnect_delay)
                time.sleep(args.reconnect_delay)
                continue
            frame_buffer.clear()

        ret, frame = cap.read()
        if not ret:
            log.warning("Stream read failed, reconnecting in %.1fs …", args.reconnect_delay)
            cap.release()
            cap = None
            time.sleep(args.reconnect_delay)
            continue

        processed = preprocess(frame)
        frame_buffer.append((processed, frame))
        if len(frame_buffer) > args.frame_gap + 1:
            frame_buffer.pop(0)

        if len(frame_buffer) < args.frame_gap + 1:
            continue  # not enough frames yet

        # --- motion check ---
        older_proc, older_raw = frame_buffer[0]
        newer_proc, newer_raw = frame_buffer[-1]
        score = motion_score(older_proc, newer_proc, args.pixel_threshold)

        now = time.time()
        if score < args.area_threshold or now < cooldown_until:
            continue

        log.info("Motion detected! Score=%.4f (threshold=%.4f)", score, args.area_threshold)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        event_dir = OUTPUT_DIR / timestamp
        event_dir.mkdir(parents=True, exist_ok=True)

        initial_path = event_dir / "initial.jpg"
        second_path = event_dir / "second.jpg"
        cv2.imwrite(str(initial_path), older_raw)
        cv2.imwrite(str(second_path), newer_raw)
        log.info("Saved frames to %s", event_dir)

        # --- AI classification ---
        error = None
        raw_response = ""
        person = False
        try:
            person, raw_response = classify_person(second_path, args.model)
        except Exception as exc:
            error = str(exc)
            log.warning("Unexpected error during classification: %s", error)

        result_str = "PERSON DETECTED" if person else "no person"
        log.info("Classification result: %s", result_str)

        video_path = None
        slack_posted = False
        if person:
            video_path = capture_video(event_dir, args.video_duration)
            if video_path:
                log.info("Sending Slack alert …")
                slack_posted = send_slack_alert(second_path, video_path, timestamp)

        event_path = save_event(
            event_dir, timestamp, args.model, score, args,
            raw_response, person, video_path, error, slack_posted=slack_posted,
        )
        log.info("Event saved: %s", event_path)

        # --- start cooldown AFTER AI returns ---
        cooldown_until = time.time() + args.cooldown
        log.info("Cooldown active for %.1fs", args.cooldown)

        # clear buffer so stale frames don't immediately re-trigger
        frame_buffer.clear()

    if cap:
        cap.release()
    log.info("Detector stopped.")


if __name__ == "__main__":
    check_slack_env()
    args = parse_args()
    log.info(
        "Starting detector | model=%s frame-gap=%d pixel-threshold=%d "
        "area-threshold=%.3f cooldown=%.1fs",
        args.model, args.frame_gap, args.pixel_threshold,
        args.area_threshold, args.cooldown,
    )
    run(args)
