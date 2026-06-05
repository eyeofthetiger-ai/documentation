# EyeOfTheTiger Documentation

Welcome to the official documentation for **EyeOfTheTiger** — an AI-ready camera that connects directly to your models out of the box.

EyeOfTheTiger runs an HTTP camera server and a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server, letting AI assistants like Claude capture images, describe scenes, detect motion, and trigger actions — all from your local network.

## What's Here

| Guide | Description |
|---|---|
| [Connect to the Portal](connect-to-portal.md) | Link your camera to the cloud portal for remote access, REST API, and MCP |
| [Integrate with Anthropic](integrate-with-anthropic.md) | Connect EyeOfTheTiger to Claude via Claude Code or Claude Desktop |
| [Integrate with OpenAI](integrate-with-openai.md) | Use EyeOfTheTiger with OpenAI models |
| [Integrate with Google](integrate-with-google.md) | Connect to Google AI tools |
| [Integrate with Ollama](integrate-with-ollama.md) | Run local models against your camera feed |
| [Integrate with OpenClaw](integrate-with-openclaw.md) | Use EyeOfTheTiger through the OpenClaw platform |

## Getting Started

Before following any integration guide, make sure your EyeOfTheTiger device is set up and on your network. Once it is, the API and MCP server will be available at:

```text
http://eyeofthetiger.local/
```

You can verify it's running by visiting:

```text
http://eyeofthetiger.local/docs
```

## Examples

Looking for ready-to-run projects built on EyeOfTheTiger? Check out the [examples](https://github.com/eyeofthetiger-ai/examples) repository, which includes projects like motion detection, daily timelapse, and person-spotted notifications.
