# Connect Your Camera to the EyeOfTheTiger Portal

The EyeOfTheTiger portal lets you access your camera remotely — from anywhere,
not just your local network. Once connected, you can capture images through the
web dashboard, the REST API, or an AI assistant via the built-in MCP server.

## 1. Create an account and add your camera

1. Open the portal: **https://platform.eyeofthetiger.ai**
2. Sign up using the **invite code** from your order confirmation email.
3. On the dashboard, click **Add camera**, give it a name, and click **Add**.
4. Copy the **Device ID** and **Device Token** — the token is shown once and
   cannot be retrieved again.

## 2. Configure your camera

Open your camera's setup page in a browser (it must be on the same network as
you):

```
http://eyeofthetiger.local/setup
```

Under **Remote Portal**, fill in:

| Field | Value |
|---|---|
| Platform URL | `wss://platform.eyeofthetiger.ai/device/ws` |
| Device ID | The ID you copied in step 1 |
| Device Token | The token you copied in step 1 |
| Enable | ✓ |

Click **Save**. The status indicator should change to **Connected** within a few
seconds.

## 3. Verify in the dashboard

Reload the portal dashboard. Your camera should appear as **online**.

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
      "camera_id": "cam_a1b2c3d4e5",
      "display_name": "Front Door",
      "status": "online",
      "last_seen": "2026-06-05T14:32:00Z"
    }
  ]
}
```

### Get an image

Triggers a capture and returns the JPEG bytes directly. Blocks until the image
is ready (up to ~45 seconds). The camera must be online.

```bash
curl https://platform.eyeofthetiger.ai/api/v1/cameras/cam_a1b2c3d4e5/image \
  -H "x-api-key: YOUR_API_KEY" \
  --fail-with-body \
  -o capture.jpg
```

`--fail-with-body` makes curl exit with an error if the response is not 2xx
(e.g. camera offline, timeout), so you don't silently save a JSON error as a
`.jpg`. Open `capture.jpg` to see the result.

---

## MCP server (for AI assistants)

The portal exposes a hosted MCP server at `/api/mcp`. No local installation
required — just add it to your AI client config with your API key.

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

### Available tools

| Tool | Description |
|---|---|
| `list_cameras` | List all your cameras with online/offline status |
| `capture_image` | Capture a photo from a camera and return the image |
