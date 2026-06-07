# Minimal Examples — Local

One tiny script per operation, each saving its result into its own folder. They
talk straight to the device on your network — no account or API key.

| Folder | What it does |
|---|---|
| [`api-capture/`](api-capture/) | `capture.sh` → `GET /v1/image` → `image.jpg` |
| [`api-record/`](api-record/) | `record.sh` → start/stop a clip → `recording.mp4` |
| [`mcp-capture/`](mcp-capture/) | `capture.py` → MCP `take_snapshot` → `image.jpg` |
| [`mcp-record/`](mcp-record/) | `record.py` → MCP `record_video` → `recording.mp4` |

The device must be on your network at `http://eyeofthetiger.local`.

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

For a live view, open `http://eyeofthetiger.local/v1/stream` in a browser.
