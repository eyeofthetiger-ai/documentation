#!/usr/bin/env python3
"""Motion descriptor: detects motion in an MJPEG stream and describes events using Ollama."""

import argparse
import base64
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import requests

STREAM_URL = "http://eyeofthetiger.local/stream.mjpg"
OLLAMA_URL = "http://localhost:11434/api/generate"
EVENTS_DIR = Path(__file__).parent.parent / "output" / "events"
OLLAMA_PROMPT = (
    "Describe what is happening in this image. Focus on people, animals, "
    "objects, and visible actions. Be concise and factual."
)

running = True


def handle_sigint(sig, frame):
    global running
    print("\n[descriptor] Shutting down...")
    running = False


def open_capture(url: str) -> cv2.VideoCapture:
    print(f"[descriptor] Connecting to stream: {url}")
    cap = cv2.VideoCapture(url)
    return cap


def preprocess(frame: np.ndarray, scale: float = 0.25) -> np.ndarray:
    small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (21, 21), 0)


def motion_score(a: np.ndarray, b: np.ndarray, pixel_thresh: int) -> float:
    diff = cv2.absdiff(a, b)
    changed = np.sum(diff > pixel_thresh)
    return changed / diff.size


def describe_image(image_path: Path, model: str) -> str:
    print(f"[descriptor] Requesting description from Ollama ({model})...")
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    payload = {
        "model": model,
        "prompt": OLLAMA_PROMPT,
        "images": [encoded],
        "stream": True,
    }
    try:
        tokens = []
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    tokens.append(chunk.get("response", ""))
                    if chunk.get("done"):
                        break
        return "".join(tokens).strip()
    except requests.exceptions.RequestException as e:
        return f"ERROR: {e}"


def save_event(event_dir: Path, initial: np.ndarray, second: np.ndarray,
               score: float, args: argparse.Namespace) -> Path:
    event_dir.mkdir(parents=True, exist_ok=True)
    initial_path = event_dir / "initial.jpg"
    second_path = event_dir / "second.jpg"
    cv2.imwrite(str(initial_path), initial)
    cv2.imwrite(str(second_path), second)

    description = describe_image(second_path, args.model)
    if description.startswith("ERROR:"):
        print(f"[descriptor] Ollama error: {description}")
    else:
        print(f"[descriptor] Description: {description}")

    event = {
        "timestamp": event_dir.name,
        "model": args.model,
        "score": round(score, 6),
        "pixel_threshold": args.pixel_threshold,
        "area_threshold": args.area_threshold,
        "frame_gap": args.frame_gap,
        "cooldown": args.cooldown,
        "initial_frame": "initial.jpg",
        "second_frame": "second.jpg",
        "description": description,
    }
    with open(event_dir / "event.json", "w") as f:
        json.dump(event, f, indent=2)

    print(f"[descriptor] Event saved: {event_dir}")
    return event_dir


def run(args: argparse.Namespace):
    signal.signal(signal.SIGINT, handle_sigint)
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)

    frame_buffer: list[np.ndarray] = []
    proc_buffer: list[np.ndarray] = []
    last_event_time = 0.0

    cap = open_capture(STREAM_URL)

    while running:
        if not cap.isOpened():
            print("[descriptor] Stream not open, retrying in 3s...")
            time.sleep(3)
            cap = open_capture(STREAM_URL)
            continue

        ret, frame = cap.read()
        if not ret:
            print("[descriptor] Failed to read frame, reconnecting in 3s...")
            cap.release()
            time.sleep(3)
            cap = open_capture(STREAM_URL)
            frame_buffer.clear()
            proc_buffer.clear()
            continue

        processed = preprocess(frame)
        frame_buffer.append(frame)
        proc_buffer.append(processed)

        if len(frame_buffer) > args.frame_gap + 1:
            frame_buffer.pop(0)
            proc_buffer.pop(0)

        if len(proc_buffer) < args.frame_gap + 1:
            continue

        older_proc = proc_buffer[0]
        newer_proc = proc_buffer[-1]
        score = motion_score(older_proc, newer_proc, args.pixel_threshold)

        now = time.time()
        if score >= args.area_threshold and (now - last_event_time) >= args.cooldown:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print(f"[descriptor] Motion detected! score={score:.4f}, saving event {ts}")
            event_dir = EVENTS_DIR / ts
            save_event(event_dir, frame_buffer[0], frame_buffer[-1], score, args)
            last_event_time = time.time()

    cap.release()
    print("[descriptor] Stopped.")


def main():
    parser = argparse.ArgumentParser(description="MJPEG motion descriptor using Ollama")
    parser.add_argument("--model", default="gemma4", help="Ollama vision model (default: gemma4)")
    parser.add_argument("--frame-gap", type=int, default=10,
                        help="Number of frames between comparison pair (default: 10)")
    parser.add_argument("--pixel-threshold", type=int, default=25,
                        help="Per-pixel diff value to count as changed (default: 25)")
    parser.add_argument("--area-threshold", type=float, default=0.02,
                        help="Fraction of changed pixels to trigger event (default: 0.02 = 2%%)")
    parser.add_argument("--cooldown", type=float, default=30.0,
                        help="Seconds between events (default: 30)")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
