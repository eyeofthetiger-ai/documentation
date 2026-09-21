# Connect Your Camera to the EyeOfTheTiger Portal

The EyeOfTheTiger portal lets you access your camera remotely, from anywhere
you have internet access, not just your local network. Once connected, you can
capture images through the web dashboard, the REST API, or an AI assistant via
the built-in MCP server.

## 1. Get your camera's Device ID and Token

Open your camera's setup page in a browser (it must be on the same network as
you):

```
http://eyeofthetiger.local/setup
```

Under **Remote Portal**, your camera has already generated its own identity,
there's nothing to configure here:

| Field | Value |
|---|---|
| Device ID | Generated automatically, e.g. `eot-a3f9c2d1` |
| Device Token | Click **Show** to reveal it |

Copy both values. The camera already knows how to reach the platform (no
Platform URL to set), so this page is read-only unless you're pointing a
camera at a non-production gateway.

## 2. Create an account and claim your camera

1. Open the portal: **https://platform.eyeofthetiger.ai**
2. Sign up using the **invite code** from your order confirmation email.
3. On the dashboard, click **Add camera**, give it a name, paste in the
   **Device ID** and **Device Token** from step 1, and click **Add**.

The status indicator on the camera's setup page should change to
**Connected** within a few seconds.

## 3. Verify in the dashboard

Reload the portal dashboard. Your camera should appear as **online**.

## Giving away or re-pairing a camera

Selling or handing off a camera? On its setup page, click **Generate new
token**, then have the new owner repeat steps 1 and 2 above with the fresh
Device ID and Token to claim it under their own account. The previous owner
loses access as soon as the new owner completes step 2, generating a new
token on its own doesn't evict anyone until the camera is actually
re-claimed.

---

## REST API

Generate an API key in the portal under **Settings → API Keys**, then use it
with the `x-api-key` header.

### List cameras

```bash
curl https://platform.eyeofthetiger.ai/api/v1/cameras \
  -H "x-api-key: YOUR_API_KEY"
```

```json
{
  "cameras": [
    {
      "camera_id": "eot-a3f9c2d1",
      "display_name": "Front Door",
      "status": "online",
      "last_seen": "2026-06-05T14:32:00Z"
    }
  ]
}
```

### Take a snapshot

Triggers a snapshot on the camera. Blocks until the image is ready (up to ~45
seconds), then redirects (302) to a short-lived signed JPEG URL. The camera
must be online.

```bash
curl -L https://platform.eyeofthetiger.ai/api/v1/cameras/eot-a3f9c2d1/snapshot \
  -H "x-api-key: YOUR_API_KEY" \
  --fail-with-body \
  -o capture.jpg
```

`-L` follows the redirect to the signed JPEG URL.

`--fail-with-body` makes curl exit with an error if the response is not 2xx
(e.g. camera offline, timeout), so you don't silently save a JSON error as a
`.jpg`. Open `capture.jpg` to see the result.

---

## MCP server (for AI assistants)

The portal exposes a hosted MCP server at `/api/mcp`. No local installation is
required. Add the server to your AI client config with your API key.

### Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "eyeofthetiger": {
      "type": "http",
      "url": "https://platform.eyeofthetiger.ai/api/mcp",
      "headers": {
        "x-api-key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add --transport http eyeofthetiger \
  https://platform.eyeofthetiger.ai/api/mcp \
  --header "x-api-key: YOUR_API_KEY"
```

### Test it

Once configured, try this prompt:

```
Using eyeofthetiger, capture an image from my camera and describe what you see.
```

### Audio and live-stream (REST, not MCP)

The five MCP tools above cover the core operations. For the new audio and
live-stream endpoints, use the REST API directly with the same `x-api-key`:

```bash
# Audio requires a USB microphone. Check get_status first
curl https://platform.eyeofthetiger.ai/api/v1/cameras/eot-a3f9c2d1/status \
  -H "x-api-key: $API_KEY" | jq .status.microphone.connected
# → true, then:
curl -L "https://platform.eyeofthetiger.ai/api/v1/cameras/eot-a3f9c2d1/audio/clip?duration_s=10" \
  -H "x-api-key: $API_KEY" --fail-with-body -o clip.aac

# Live stream: device pushes WHIP to Cloudflare and you watch via WHEP
curl -X POST https://platform.eyeofthetiger.ai/api/v1/cameras/eot-a3f9c2d1/live-stream/start \
  -H "x-api-key: $API_KEY"
curl https://platform.eyeofthetiger.ai/api/v1/cameras/eot-a3f9c2d1/live-stream \
  -H "x-api-key: $API_KEY" # → {webrtc_playback_url, live_input_uid}
# Open an RTCPeerConnection and POST your SDP offer to webrtc_playback_url;
# stop with POST …/live-stream/stop when done.
curl -X POST https://platform.eyeofthetiger.ai/api/v1/cameras/eot-a3f9c2d1/live-stream/stop \
  -H "x-api-key: $API_KEY"

# Also available: POST /audio/continuous-recording/start and stop,
# POST /audio/continuous-recording/segment-length?segment_seconds=…,
# POST /audio/continuous-recording/limit?max_bytes=… (video and audio share
# one disk quota), and ?kind=audio_clip|audio_continuous in library browsing.
# Cloud apps: see [Apps](../local/apps/README.md) for CloudAppRunner (Cloud Run
# per camera, deployment_target cloud or both, cpu-small only).
```

### Available tools

| Tool | Description |
|---|---|
| `list_cameras` | List all your cameras with online/offline status |
| `take_snapshot` | Take a snapshot from a camera and return the image |
| `record_video` | Record a fixed-length clip and return a download URL for the MP4 |
| `get_status` | Full device picture, including `camera` (`local_streaming`, `live_stream.streaming`, clip/continuous, quality) and `microphone` (`connected`, busy). Mirrors `GET /api/v1/cameras/:id/status`. |
| `set_quality` | Set the camera quality preset (one tier for stills + clips) |
| `register_camera` | Pair a camera: `device_id` + `device_token` (+ optional `display_name`) |
| `get_api_reference` | Return the REST endpoint list (also at `https://platform.eyeofthetiger.ai/api/docs`) |
