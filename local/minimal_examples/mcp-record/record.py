"""Record a clip via the local MCP server, then save it as recording.mp4."""

import asyncio
import json

import httpx
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

DEVICE = "http://eyeofthetiger.local"


async def main():
    print('Recording clip...')
    # Trailing slash matters: the device serves MCP at /mcp/ (a request to
    # /mcp redirects, which the streamable-HTTP client won't follow → it hangs).
    async with streamablehttp_client(f"{DEVICE}/mcp/") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # record_video returns a download URL, not the video itself.
            result = await session.call_tool("record_video", {"duration_s": 10})

    url = json.loads(result.content[0].text)["download_url"]
    clip = httpx.get(url, timeout=60).content
    with open("recording.mp4", "wb") as f:
        f.write(clip)
    print("Saved recording.mp4")


asyncio.run(main())
