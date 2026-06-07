"""Slack alert sender using the current file upload API."""

import logging
import os
import sys
from pathlib import Path

import requests

SLACK_API_BASE = "https://slack.com/api"

log = logging.getLogger(__name__)


def check_slack_env():
    missing = [v for v in ("SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID")
               if not os.environ.get(v)]
    if missing:
        print(
            "ERROR: Missing required environment variable(s): "
            + ", ".join(missing)
            + "\n\nSet them before running:\n"
            "  export SLACK_BOT_TOKEN=xoxb-your-token-here\n"
            "  export SLACK_CHANNEL_ID=CXXXXXXXXXX\n",
            file=sys.stderr,
        )
        sys.exit(1)


def _get_upload_url(headers: dict, filename: str, size: int) -> tuple[str, str] | None:
    """Return (upload_url, file_id) or None on failure.
    NOTE: files.getUploadURLExternal requires form-encoded params (data=), not JSON.
    Sending JSON returns an invalid_arguments error from Slack."""
    try:
        resp = requests.post(
            f"{SLACK_API_BASE}/files.getUploadURLExternal",
            headers=headers,
            data={"filename": filename, "length": size},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        log.warning("Slack getUploadURLExternal failed: %s", exc)
        return None

    if not data.get("ok"):
        log.warning("Slack getUploadURLExternal error: %s", data.get("error"))
        return None

    return data["upload_url"], data["file_id"]


def _upload_file(upload_url: str, image_path: Path) -> bool:
    try:
        with open(image_path, "rb") as fh:
            resp = requests.post(upload_url, data=fh, timeout=60)
        resp.raise_for_status()
        return True
    except requests.RequestException as exc:
        log.warning("Slack file upload failed for %s: %s", image_path.name, exc)
        return False


def send_slack_alert(image_path: Path, video_path: Path, timestamp: str) -> bool:
    """Upload a still image and a video to Slack as a single channel message.
    Returns True if posted successfully."""
    token = os.environ["SLACK_BOT_TOKEN"]
    channel = os.environ["SLACK_CHANNEL_ID"]
    headers = {"Authorization": f"Bearer {token}"}

    file_ids = []
    for path in (image_path, video_path):
        result = _get_upload_url(headers, path.name, path.stat().st_size)
        if result is None:
            return False
        upload_url, file_id = result
        if not _upload_file(upload_url, path):
            return False
        file_ids.append(file_id)
        log.info("Uploaded %s to Slack", path.name)

    try:
        resp = requests.post(
            f"{SLACK_API_BASE}/files.completeUploadExternal",
            headers=headers,
            json={
                "files": [{"id": fid} for fid in file_ids],
                "channel_id": channel,
                "initial_comment": f"Person spotted at {timestamp}",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        log.warning("Slack completeUploadExternal failed: %s", exc)
        return False

    if not data.get("ok"):
        log.warning("Slack completeUploadExternal error: %s", data.get("error"))
        return False

    log.info("Slack alert posted for event %s", timestamp)
    return True
