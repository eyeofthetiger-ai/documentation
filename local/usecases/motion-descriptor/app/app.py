#!/usr/bin/env python3
"""Event browser for motion descriptor events."""

import json
from pathlib import Path

from flask import Flask, abort, render_template, send_file

EVENTS_DIR = Path(__file__).parent.parent / "output" / "events"

app = Flask(__name__)


def load_events() -> list[dict]:
    events = []
    if not EVENTS_DIR.exists():
        return events
    for folder in sorted(EVENTS_DIR.iterdir(), reverse=True):
        if not folder.is_dir():
            continue
        json_path = folder / "event.json"
        if not json_path.exists():
            continue
        with open(json_path) as f:
            data = json.load(f)
        data["folder"] = folder.name
        events.append(data)
    return events


@app.route("/")
def index():
    events = load_events()
    return render_template("index.html", events=events)


@app.route("/event/<timestamp>")
def event_detail(timestamp: str):
    event_dir = EVENTS_DIR / timestamp
    if not event_dir.is_dir():
        abort(404)
    json_path = event_dir / "event.json"
    if not json_path.exists():
        abort(404)
    with open(json_path) as f:
        event = json.load(f)
    event["folder"] = timestamp
    events = load_events()
    return render_template("index.html", events=events, selected=event)


@app.route("/image/<timestamp>/<filename>")
def serve_image(timestamp: str, filename: str):
    if "/" in timestamp or "/" in filename:
        abort(400)
    image_path = EVENTS_DIR / timestamp / filename
    if not image_path.exists() or image_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
        abort(404)
    return send_file(image_path, mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
