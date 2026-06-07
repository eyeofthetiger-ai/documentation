# Minimal Examples — Cloud

Smoke tests that exercise every endpoint of the EyeOfTheTiger **cloud platform**
developer API, plus the hosted MCP server. Use these to confirm a camera is
reachable through the platform from anywhere.

The same operations are available over the REST API and over MCP:

| | REST (`/api/v1/cameras/{id}`) | MCP tool |
|---|---|---|
| Still image | `GET /image` | `take_snapshot` |
| Start recording | `POST /start` | `record_video` |
| Stop recording | `POST /stop` | (handled by `record_video`) |
| Download clip | `GET /recording` | `get_recording` |
| Live preview | `GET /stream` | — |

Image and recording responses **302-redirect** to a signed storage URL, so the
bytes stream straight from object storage (`curl -L` follows it automatically).

## Prerequisites

1. A camera linked to your account and showing **online** in the portal.
2. A developer **API key** (`eott_…`) from the portal **Settings** page.
3. Your **camera id** (`cam_…`), shown on the dashboard.

```bash
export API_KEY=eott_xxxxxxxx
export CAMERA_ID=cam_xxxxxxxx
# PORTAL_URL defaults to the hosted platform; override if self-hosting.
```

## REST test (bash)

```bash
./test-endpoints.sh
```

Captures a still and a short clip (opening each), then checks the live stream.
Note: the API stream needs the `x-api-key` header, so a browser can't open it
directly — the script confirms bytes flow with `curl`, then opens the **portal
dashboard** camera page for the visual preview (which streams over your
logged-in session).

## MCP test (python)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python mcp_test.py
```

Connects to the hosted MCP at `/api/mcp` with your API key, calls
`take_snapshot` (opens the image) and `record_video` (downloads and opens the
clip). This is also the server you'd add to Claude Desktop / other MCP clients.
