#!/usr/bin/env python3
"""Person-detection notifier: polls the still-image endpoint for motion, then uses
Ollama to classify whether a person is present and posts to Slack."""

import argparse
import base64
import json
import logging
import signal
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import requests

from slack_poster import check_slack_env, send_slack_alert

IMAGE_URL = "http://eyeofthetiger.local/v1/snapshot"
CLIP_URL = "http://eyeofthetiger.local/v1/clip"
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
    p.add_argument("--poll-interval", type=float, default=1.0,
                   help="Seconds between image fetches (default: 1.0)")
    p.add_argument("--pixel-threshold", type=int, default=25,
                   help="Per-pixel difference threshold 0-255 (default: 25)")
    p.add_argument("--area-threshold", type=float, default=0.02,
                   help="Fraction of changed pixels that triggers a check (default: 0.02)")
    p.add_argument("--cooldown", type=float, default=10.0,
                   help="Seconds to wait after AI returns before triggering again (default: 10)")
    p.add_argument("--model", default="gemma4",
                   help="Ollama vision model to use (default: gemma4)")
    p.add_argument("--reconnect-delay", type=float, default=5.0,
                   help="Seconds to wait after a fetch failure before retrying (default: 5)")
    p.add_argument("--video-duration", type=float, default=10.0,
                   help="Seconds of video to capture and post when a person is confirmed (default: 10)")
    return p.parse_args()


def fetch_frame() -> np.ndarray | None:
    """Fetch one JPEG from the device and decode it as a BGR frame."""
    try:
        resp = requests.get(IMAGE_URL, timeout=10)
        if resp.status_code != 200:
            return None
        arr = np.frombuffer(resp.content, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except requests.RequestException as exc:
        log.warning("Image fetch failed: %s", exc)
        return None


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
    """Request a fixed-length clip from the device and download the MP4."""
    log.info("Recording %.1fs clip …", duration)
    try:
        resp = requests.get(CLIP_URL, params={"duration_s": int(duration)}, timeout=duration + 30)
        if resp.status_code != 200:
            log.warning("Failed to record clip: %s", resp.status_code)
            return None
        video_path = event_dir / "event.mp4"
        video_path.write_bytes(resp.content)
        log.info("Saved %d-byte video to %s", len(resp.content), video_path.name)
        return video_path
    except requests.RequestException as exc:
        log.warning("Failed to record clip: %s", exc)
        return None


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
        "poll_interval_s": args.poll_interval,
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


def run(args):
    global running
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    prev_frame = None
    prev_pre = None
    cooldown_until = 0.0

    log.info("Monitoring …")

    while running:
        frame = fetch_frame()
        if frame is None:
            log.warning("Could not fetch image, retrying in %.1fs …", args.reconnect_delay)
            time.sleep(args.reconnect_delay)
            continue

        processed = preprocess(frame)

        if prev_pre is None:
            prev_frame, prev_pre = frame, processed
            time.sleep(args.poll_interval)
            continue

        score = motion_score(prev_pre, processed, args.pixel_threshold)

        now = time.time()
        if score < args.area_threshold or now < cooldown_until:
            prev_frame, prev_pre = frame, processed
            time.sleep(args.poll_interval)
            continue

        log.info("Motion detected! Score=%.4f (threshold=%.4f)", score, args.area_threshold)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        event_dir = OUTPUT_DIR / timestamp
        event_dir.mkdir(parents=True, exist_ok=True)

        initial_path = event_dir / "initial.jpg"
        second_path = event_dir / "second.jpg"
        cv2.imwrite(str(initial_path), prev_frame)
        cv2.imwrite(str(second_path), frame)
        log.info("Saved frames to %s", event_dir)

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

        cooldown_until = time.time() + args.cooldown
        log.info("Cooldown active for %.1fs", args.cooldown)

        prev_frame, prev_pre = None, None
        time.sleep(args.poll_interval)

    log.info("Detector stopped.")


if __name__ == "__main__":
    check_slack_env()
    args = parse_args()
    log.info(
        "Starting detector | model=%s poll-interval=%.1fs pixel-threshold=%d "
        "area-threshold=%.3f cooldown=%.1fs",
        args.model, args.poll_interval, args.pixel_threshold,
        args.area_threshold, args.cooldown,
    )
    run(args)
