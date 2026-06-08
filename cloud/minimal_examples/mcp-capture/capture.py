"""Capture a still image via the hosted MCP server, saved as image.jpg."""

import asyncio
import base64
import os
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

PORTAL = "https://portal-598626659536.europe-west2.run.app"

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
    headers = {"x-api-key": API_KEY}
    async with streamablehttp_client(f"{PORTAL}/api/mcp", headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("take_snapshot", {"camera_id": CAMERA_ID})

    for item in result.content:
        if item.type == "image":
            with open("image.jpg", "wb") as f:
                f.write(base64.b64decode(item.data))
            print("Saved image.jpg")


asyncio.run(main())
