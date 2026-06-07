#!/usr/bin/env python3
"""Minimal test of the EyeOfTheTiger hosted MCP server (cloud).

Connects to the platform's MCP endpoint with your developer API key, then:
  • calls `take_snapshot` and opens the returned image
  • calls `record_video`, then downloads the clip and opens it

Setup:
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    export API_KEY=eott_xxxxxxxx
    export CAMERA_ID=cam_xxxxxxxx
    python mcp_test.py
"""

import asyncio
import base64
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

PORTAL_URL = os.environ.get(
    "PORTAL_URL", "https://portal-598626659536.europe-west2.run.app"
)
API_KEY = os.environ.get("API_KEY")
CAMERA_ID = os.environ.get("CAMERA_ID")
MCP_URL = f"{PORTAL_URL}/api/mcp"


def open_target(path: str) -> None:
    """Open a file with the OS default handler."""
    for cmd in (["xdg-open"], ["open"], ["cmd", "/c", "start", ""]):
        if subprocess.run(["which", cmd[0]], capture_output=True).returncode == 0:
            subprocess.Popen([*cmd, path])
            return
    print(f"  open manually: {path}")


async def main() -> None:
    if not API_KEY or not CAMERA_ID:
        sys.exit("Set API_KEY and CAMERA_ID environment variables first.")

    headers = {"x-api-key": API_KEY}
    out = Path(tempfile.mkdtemp())

    async with streamablehttp_client(MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Tools:", ", ".join(t.name for t in tools.tools))

            # 1) Snapshot — the image comes back inline.
            print("\ntake_snapshot ...")
            res = await session.call_tool("take_snapshot", {"camera_id": CAMERA_ID})
            for c in res.content:
                if getattr(c, "type", None) == "image":
                    path = out / "snapshot.jpg"
                    path.write_bytes(base64.b64decode(c.data))
                    print(f"  saved {path}")
                    open_target(str(path))
                elif getattr(c, "type", None) == "text":
                    print(f"  {c.text}")

            # 2) Record — the tool returns a download URL; fetch + open it.
            print("\nrecord_video (5s) ...")
            res = await session.call_tool(
                "record_video", {"camera_id": CAMERA_ID, "duration_s": 5}
            )
            for c in res.content:
                if getattr(c, "type", None) == "text":
                    print(f"  {c.text}")

            url = f"{PORTAL_URL}/api/v1/cameras/{CAMERA_ID}/recording"
            async with httpx.AsyncClient(follow_redirects=True, timeout=60) as http:
                for _ in range(20):
                    r = await http.get(url, headers=headers)
                    if r.status_code == 200:
                        path = out / "recording.mp4"
                        path.write_bytes(r.content)
                        print(f"  saved {path} ({len(r.content)} bytes)")
                        open_target(str(path))
                        break
                    await asyncio.sleep(2)
                else:
                    print("  recording not ready in time")

    print(f"\nDone. Files in {out}")


if __name__ == "__main__":
    asyncio.run(main())
