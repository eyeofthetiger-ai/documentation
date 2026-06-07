# Minimal Examples — Local

Smoke tests that exercise every endpoint of a **local** EyeOfTheTiger camera on
your network. No account or API key needed — these talk straight to the device.

The same five operations are available over HTTP and over MCP:

| | HTTP (device API) | MCP tool |
|---|---|---|
| Still image | `GET /v1/image` | `take_snapshot` |
| Start recording | `POST /v1/start` | `record_video` |
| Stop recording | `POST /v1/stop` | (handled by `record_video`) |
| Download clip | `GET /v1/recording` | `get_recording` |
| Live preview | `GET /v1/stream` | — |

## Prerequisites

- An EyeOfTheTiger camera powered on and on the same network, reachable at
  `http://eyeofthetiger.local` (or use its IP).

## HTTP test (bash)

Captures a still, records a short clip, and opens the live stream — opening
each result so you can confirm it works.

```bash
./test-endpoints.sh
# against a different host / longer clip:
BASE=http://192.168.1.50:8000/v1 RECORD_SECONDS=8 ./test-endpoints.sh
```

## MCP test (python)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python mcp_test.py
# against a different host:
DEVICE_URL=http://192.168.1.50:8000 python mcp_test.py
```

It calls `take_snapshot` (opens the image) and `record_video` (downloads and
opens the clip).
