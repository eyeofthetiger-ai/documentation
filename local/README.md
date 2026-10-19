# EyeOfTheTiger Documentation

Welcome to the official documentation for **EyeOfTheTiger**, an AI-ready camera
that connects directly to your models out of the box.

EyeOfTheTiger runs an HTTP camera server and a Model Context Protocol (MCP)
server, which let AI assistants like Claude capture images, describe scenes,
detect motion, and trigger actions, all from your local network.

## What's Here

| Guide | Description |
|---|---|
| [Integrate with Anthropic](integrations/integrate-with-anthropic.md) | Connect EyeOfTheTiger to Claude via Claude Code or Claude Desktop |
| [Integrate with OpenAI](integrations/integrate-with-openai.md) | Use EyeOfTheTiger with OpenAI models |
| [Integrate with Google](integrations/integrate-with-google.md) | Connect to Google AI tools |
| [Integrate with Ollama](integrations/integrate-with-ollama.md) | Run local models against your camera feed |
| [Integrate with OpenClaw](integrations/integrate-with-openclaw.md) | Use EyeOfTheTiger through the OpenClaw platform |
| [Apps](apps/README.md) | What apps are, where they run (on your EOT-1 or in the cloud), and how to build one |
| [Marketplace](../cloud/marketplace.md) | Install ready-made apps, pay with credits, and publish your own |

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

[`minimal_examples/`](minimal_examples/) has quick smoke tests, including a bash script
and an MCP script that capture an image and record a short clip against your device,
which is useful for confirming that everything works.

## Use cases

[`usecases/`](usecases/) has full, ready-to-run projects built on EyeOfTheTiger,
including motion detection, a daily timelapse, person-spotted notifications, and more.

## Apps

An app gives your EOT-1 a job and keeps doing it, running either on the EOT-1
itself or in the cloud. [`apps/`](apps/README.md) explains both and how to
build an on-device app, with a ready-to-install minimal example in
[`apps/test-app/`](apps/test-app/). To install ready-made apps or publish
your own, see the [Marketplace](../cloud/marketplace.md).

## Live streaming and audio

- **Live stream**: `POST /live-stream/start` and `POST /live-stream/stop` on-device,
  and `POST /api/v1/cameras/:id/live-stream/start`, `POST /api/v1/cameras/:id/live-stream/stop`,
  and `GET /api/v1/cameras/:id/live-stream` (playback URL) in the cloud. Local preview remains at
  `GET /live-stream.mjpg`.
- **USB microphone**: parallel audio API with `GET /audio/clip`,
  `GET /audio/stream.aac`, and `POST /audio/continuous-recording/*`.
  `GET /status` now returns `{camera, microphone}`. See `GET /status` and the API
  references at `http://eyeofthetiger.local/docs` for local and
  `https://platform.eyeofthetiger.ai/api/docs` for cloud.
- **Status shape**: `camera.local_streaming` is the LAN MJPEG preview and
  `camera.live_stream.streaming` indicates whether remote live streaming is active.
  `microphone.connected` must be true before any `audio/*` routes will succeed.
