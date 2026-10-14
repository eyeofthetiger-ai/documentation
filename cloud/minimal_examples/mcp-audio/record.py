"""Record an audio clip via the hosted MCP server, then save it as recording.aac."""

import asyncio
import json
import os
from pathlib import Path

import httpx
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

PORTAL = "https://platform.eyeofthetiger.ai"

_env_file = Path(__file__).parent.parent / ".env"
_env_example = _env_file.parent / ".env.example"
if not _env_file.exists():
    print(f"No .env file found. Run: cp {_env_example} {_env_file}  then fill in your values.")
    raise SystemExit(1)

for _line in _env_file.read_text().splitlines():
    _line = _line.strip()
    if _line and not _line.startswith("#") and "=" in _line:
        _k, _, _v = _line.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip())

API_KEY = os.environ.get("API_KEY", "")
CAMERA_ID = os.environ.get("CAMERA_ID", "")

if "REPLACE_ME" in API_KEY or "REPLACE_ME" in CAMERA_ID:
    print("Please edit cloud/minimal_examples/.env and replace API_KEY and CAMERA_ID with your values.")
    raise SystemExit(1)

async def main():
    print("Recording audio clip...")
    headers = {"x-api-key": API_KEY}
    async with streamablehttp_client(f"{PORTAL}/api/mcp", headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Fails with a clear error if no USB microphone is attached.
            result = await session.call_tool(
                "record_audio_clip", {"camera_id": CAMERA_ID, "duration_s": 10}
            )

    if result.isError:
        raise SystemExit(result.content[0].text)
    url = json.loads(result.content[0].text)["download_url"]
    clip = httpx.get(url, follow_redirects=True, timeout=60).content
    with open("recording.aac", "wb") as f:
        f.write(clip)
    print("Saved recording.aac")


asyncio.run(main())
