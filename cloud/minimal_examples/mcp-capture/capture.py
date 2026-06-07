"""Capture a still image via the hosted MCP server, saved as image.jpg.

Edit the three values below first.
"""

import asyncio
import base64

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

PORTAL = "https://portal-598626659536.europe-west2.run.app"
API_KEY = "eott_REPLACE_ME"
CAMERA_ID = "cam_REPLACE_ME"


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
