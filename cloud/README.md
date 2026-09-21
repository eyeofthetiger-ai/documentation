# EyeOfTheTiger Cloud Documentation

Connect your camera to the EyeOfTheTiger platform for remote access from
anywhere. Your agents talk to the platform over HTTPS, so no VPN or
port forwarding is required.

## What's Here

| Guide | Description |
|---|---|
| [Connect to the Portal](connect-to-portal.md) | Link your camera, get an API key, test with curl and MCP |
| [Minimal examples](minimal_examples/) | Smoke-test every endpoint (bash + MCP): snapshot, clip, **audio clip**, **live-stream**, status, library, usage |
| [Apps (cloud)](../local/apps/README.md#the-contract) | Cloud apps scoped to one camera (`deployment_target: cloud` or `both`, `cpu-small` only) |

## Live streaming and audio

- Live streaming for remote viewing is now available. Use
  `POST /api/v1/cameras/:id/live-stream/start` and `stop`, and
  `GET /api/v1/cameras/:id/live-stream` for the playback URL.
- USB microphone support is now available end to end. This includes
  `GET /api/v1/cameras/:id/audio/clip`, `POST /api/v1/cameras/:id/audio/continuous-recording/*`,
  and `?kind=audio_clip|audio_continuous` in the library. Check
  `microphone.connected` from `GET /status` first.

## More coming soon

Cloud integration guides for Anthropic, OpenAI, Google, and others are in
progress and will appear here as the platform is built out. Minimal-example
scripts for the new audio and live-stream endpoints follow the same pattern as
`cloud/minimal_examples/api-capture`. See `local/minimal_examples/README.md`
for the local equivalent.
