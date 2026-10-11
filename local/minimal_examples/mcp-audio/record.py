"""Record an audio clip via the local MCP server, then save it as recording.aac."""

import asyncio
import json

import httpx
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

DEVICE = "http://eyeofthetiger.local"


async def main():
    print("Recording audio clip...")
    # Trailing slash matters: the device serves MCP at /mcp/ (a request to
    # /mcp redirects, which the streamable-HTTP client won't follow → it hangs).
    async with streamablehttp_client(f"{DEVICE}/mcp/") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Fails with a clear error if no USB microphone is attached.
            result = await session.call_tool("record_audio_clip", {"duration_s": 10})

    if result.isError:
        raise SystemExit(result.content[0].text)
    url = json.loads(result.content[0].text)["download_url"]
    clip = httpx.get(url, timeout=60).content
    with open("recording.aac", "wb") as f:
        f.write(clip)
    print("Saved recording.aac")


asyncio.run(main())
