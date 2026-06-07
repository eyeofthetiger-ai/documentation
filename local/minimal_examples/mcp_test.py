#!/usr/bin/env python3
"""Minimal test of the EyeOfTheTiger local MCP server (on the device).

Connects to the camera's MCP endpoint on your network (no API key), then:
  • calls `take_snapshot` and opens the returned image
  • calls `record_video`, then downloads the clip from the device and opens it

Setup:
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python mcp_test.py
    # or against a different host:
    DEVICE_URL=http://192.168.1.50:8000 python mcp_test.py
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

DEVICE_URL = os.environ.get("DEVICE_URL", "http://eyeofthetiger.local")
MCP_URL = f"{DEVICE_URL}/mcp"


def open_target(path: str) -> None:
    """Open a file with the OS default handler."""
    for cmd in (["xdg-open"], ["open"], ["cmd", "/c", "start", ""]):
        if subprocess.run(["which", cmd[0]], capture_output=True).returncode == 0:
            subprocess.Popen([*cmd, path])
            return
    print(f"  open manually: {path}")


async def main() -> None:
    out = Path(tempfile.mkdtemp())

    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Tools:", ", ".join(t.name for t in tools.tools))

            # 1) Snapshot — the image comes back inline.
            print("\ntake_snapshot ...")
            res = await session.call_tool("take_snapshot", {})
            for c in res.content:
                if getattr(c, "type", None) == "image":
                    path = out / "snapshot.jpg"
                    path.write_bytes(base64.b64decode(c.data))
                    print(f"  saved {path}")
                    open_target(str(path))
                elif getattr(c, "type", None) == "text":
                    print(f"  {c.text}")

            # 2) Record — the tool records, then we download GET /v1/recording.
            print("\nrecord_video (5s) ...")
            res = await session.call_tool("record_video", {"duration_s": 5})
            for c in res.content:
                if getattr(c, "type", None) == "text":
                    print(f"  {c.text}")

            url = f"{DEVICE_URL}/v1/recording"
            async with httpx.AsyncClient(timeout=60) as http:
                for _ in range(15):
                    r = await http.get(url)
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
