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
