# EyeOfTheTiger Cloud Documentation

Connect your camera to the EyeOfTheTiger platform for remote access from
anywhere. Your agents talk to the platform over HTTPS — no VPN, no
port-forwarding required.

## What's Here

| Guide | Description |
|---|---|
| [Connect to the Portal](connect-to-portal.md) | Link your camera, get an API key, test with curl and MCP |
| [Minimal examples](minimal_examples/) | Smoke-test every endpoint (bash + MCP): snapshot, clip, **audio clip**, **live-stream**, status, library, usage |
| [Apps (cloud)](../local/apps/README.md#the-contract) | `CloudAppRunner` — Cloud Run apps scoped to one camera (`deployment_target: cloud`/`both`, `cpu-small` only) |

## Live-stream & audio

- Cloud-gateway now brokers **WHIP/WHEP live-streaming via Cloudflare Stream** (`src/devices/cloudAppRunner.ts`, `portal:LiveStreamPlayer.tsx`): `POST /api/v1/cameras/:id/live-stream/start|stop` + `GET /api/v1/cameras/:id/live-stream` (WHEP URL). Bytes never flow through the gateway or portal.
- **USB microphone** support is live end-to-end: `GET /api/v1/cameras/:id/audio/clip`, `POST /api/v1/cameras/:id/audio/continuous-recording/*`, `?kind=audio_clip|audio_continuous` in the library. Check `microphone.connected` from `GET /status` first.

## More coming soon

Cloud integration guides for Anthropic, OpenAI, Google, and others are in
progress — they'll appear here as the platform is built out. Minimal-example
scripts for the new audio and live-stream endpoints follow the same pattern as
`cloud/minimal_examples/api-capture` — see `local/minimal_examples/README.md`
for the local shape.
