#!/usr/bin/env python3
"""Event browser for the motion detection recorder."""

import json
import os

from flask import Flask, abort, jsonify, render_template, send_file

EVENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "events")

app = Flask(__name__)


def load_events() -> list[dict]:
    events = []
    if not os.path.isdir(EVENTS_DIR):
        return events
    for name in sorted(os.listdir(EVENTS_DIR), reverse=True):
        folder = os.path.join(EVENTS_DIR, name)
        meta_path = os.path.join(folder, "event.json")
        if not os.path.isfile(meta_path):
            continue
        with open(meta_path) as f:
            meta = json.load(f)
        meta["id"] = name
        events.append(meta)
    return events


@app.route("/")
def index():
    events = load_events()
    return render_template("index.html", events=events)


@app.route("/api/events")
def api_events():
    return jsonify(load_events())


@app.route("/media/<event_id>/<filename>")
def media(event_id: str, filename: str):
    # Prevent path traversal
    if ".." in event_id or ".." in filename or "/" in event_id or "/" in filename:
        abort(400)
    path = os.path.join(EVENTS_DIR, event_id, filename)
    if not os.path.isfile(path):
        abort(404)
    return send_file(path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
