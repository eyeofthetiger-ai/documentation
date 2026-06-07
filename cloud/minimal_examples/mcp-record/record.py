"""Record a clip via the hosted MCP server, then save it as recording.mp4.

Edit the three values below first.
"""

import asyncio

import httpx
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
            result = await session.call_tool(
                "record_video", {"camera_id": CAMERA_ID, "duration_s": 5}
            )
            print(result.content[0].text)

    # The clip is ready; download it via the developer API.
    url = f"{PORTAL}/api/v1/cameras/{CAMERA_ID}/recording"
    clip = httpx.get(url, headers=headers, follow_redirects=True).content
    with open("recording.mp4", "wb") as f:
        f.write(clip)
    print("Saved recording.mp4")


asyncio.run(main())
