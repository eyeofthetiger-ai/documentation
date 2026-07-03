# Minimal Examples — Cloud

One tiny script per operation, each saving its result into its own folder. They
use the platform's developer API, so they work from anywhere.

| Folder | What it does |
|---|---|
| [`api-capture/`](api-capture/) | `capture.sh` → `GET /api/v1/cameras/{id}/snapshot` → `image.jpg` |
| [`api-record/`](api-record/) | `record.sh` → `GET /clip` → `recording.mp4` |
| [`mcp-capture/`](mcp-capture/) | `capture.py` → MCP `take_snapshot` → `image.jpg` |
| [`mcp-record/`](mcp-record/) | `record.py` → MCP `record_video` → `recording.mp4` |

Each script has three values to edit at the top: `PORTAL`, `API_KEY` (your
`eott_` key from the portal **Settings** page), and `CAMERA_ID`.

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
