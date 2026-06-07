"""Capture a still image via the local MCP server, saved as image.jpg."""

import asyncio
import base64

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("http://eyeofthetiger.local/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("take_snapshot", {})

    for item in result.content:
        if item.type == "image":
            with open("image.jpg", "wb") as f:
                f.write(base64.b64decode(item.data))
            print("Saved image.jpg")


asyncio.run(main())
