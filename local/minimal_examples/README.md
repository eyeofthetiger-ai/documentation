# Minimal Examples: Local

One tiny script per operation, each saving its result into its own folder. They
talk directly to the device on your local network and do not require an account
or API key.

| Folder | What it does |
|---|---|
| [`api-capture/`](api-capture/) | `capture.sh` → `GET /v1/snapshot` → `image.jpg` |
| [`api-record/`](api-record/) | `record.sh` → `GET /v1/clip` → `recording.mp4` |
| [`api-audio/`](api-audio/) | `capture.sh` → `GET /v1/audio/clip` → `recording.aac` *(requires USB microphone; returns 503 if `microphone.connected` is false)* |
| [`api-live-stream/`](api-live-stream/) | `stream.sh` → `POST /v1/live-stream/start` and `GET /v1/live-stream.mjpg` → `stream check` |
| [`mcp-capture/`](mcp-capture/) | `capture.py` → MCP `take_snapshot` → `image.jpg` |
| [`mcp-record/`](mcp-record/) | `record.py` → MCP `record_video` → `recording.mp4` |
| [`mcp-audio/`](mcp-audio/) | `capture.py` → MCP `record_audio_clip` → `recording.aac` *(same mic gate)* |

The device must be on your network at `http://eyeofthetiger.local`. Use `GET /v1/status`
to check `{camera: {local_streaming, live_stream, busy}, microphone: {connected, busy}}`
before calling any `/audio/*` route, which returns 503 without a microphone, or before
expecting `live_stream` fields.

**Bash (API):**
```bash
cd api-capture && bash capture.sh
```

**Python (MCP):**
```bash
cd mcp-capture
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python capture.py
```
