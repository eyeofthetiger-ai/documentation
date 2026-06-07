"""Record a clip via the local MCP server, then save it as recording.mp4."""

import asyncio

import httpx
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

DEVICE = "http://eyeofthetiger.local"


async def main():
    async with streamablehttp_client(f"{DEVICE}/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("record_video", {"duration_s": 5})
            print(result.content[0].text)

    # The clip is now on the device; download it.
    clip = httpx.get(f"{DEVICE}/v1/recording").content
    with open("recording.mp4", "wb") as f:
        f.write(clip)
    print("Saved recording.mp4")


asyncio.run(main())
