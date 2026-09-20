# EyeOfTheTiger Documentation

Welcome to the official documentation for **EyeOfTheTiger** — an AI-ready camera that connects directly to your models out of the box.

EyeOfTheTiger runs an HTTP camera server and a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server, letting AI assistants like Claude capture images, describe scenes, detect motion, and trigger actions — all from your local network.

## What's Here

| Guide | Description |
|---|---|
| [Integrate with Anthropic](integrations/integrate-with-anthropic.md) | Connect EyeOfTheTiger to Claude via Claude Code or Claude Desktop |
| [Integrate with OpenAI](integrations/integrate-with-openai.md) | Use EyeOfTheTiger with OpenAI models |
| [Integrate with Google](integrations/integrate-with-google.md) | Connect to Google AI tools |
| [Integrate with Ollama](integrations/integrate-with-ollama.md) | Run local models against your camera feed |
| [Integrate with OpenClaw](integrations/integrate-with-openclaw.md) | Use EyeOfTheTiger through the OpenClaw platform |
| [Apps](apps/README.md) | Run your own long-running program on-device **or in the cloud** (Cloud Run, scoped to one camera), with events reported back |

## Getting Started

Before following any integration guide, make sure your EyeOfTheTiger device is set up and on your network. Once it is, the API and MCP server will be available at:

```text
http://eyeofthetiger.local/
```

You can verify it's running by visiting:

```text
http://eyeofthetiger.local/docs
```

## Test the endpoints

[`minimal_examples/`](minimal_examples/) has quick smoke tests (a bash script and an MCP script) that capture an image and record a short clip against your device — handy for confirming everything works.

## Use cases

[`usecases/`](usecases/) has full, ready-to-run projects built on EyeOfTheTiger — motion detection, a daily timelapse, person-spotted notifications, and more.

## Apps

[`apps/`](apps/README.md) covers the apps platform: your own long-running
program on-device (built and run on your EOT-1) **or in the cloud** (a
Cloud Run service per camera via the gateway's `CloudAppRunner`). Both watch
the live stream and report structured events back, plus a full,
ready-to-install minimal example in [`apps/test-app/`](apps/test-app/).

## What's new since `main`

- **Live stream (WHIP/WHEP via Cloudflare Stream)** — `POST /live-stream/start|stop` on-device and `POST /api/v1/cameras/:id/live-stream/start|stop` + `GET /api/v1/cameras/:id/live-stream` (WHEP URL) in the cloud. Local preview stays at `GET /live-stream.mjpg`.
- **USB microphone** — parallel audio API (`GET /audio/clip`, `GET /audio/stream.aac`, `POST /audio/continuous-recording/*`). `GET /status` now returns `{camera, microphone}`; see `GET /status` and local `http://eyeofthetiger.local/docs` / cloud `https://platform.eyeofthetiger.ai/api/docs`.
- **Status shape** — `camera.local_streaming` (LAN MJPEG) vs `camera.live_stream.streaming` (WHIP); `microphone.connected` gates all `audio/*` routes.
