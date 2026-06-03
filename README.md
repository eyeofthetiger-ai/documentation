# EyeOfTheTiger Documentation

Welcome to the official documentation for **EyeOfTheTiger** — a Raspberry Pi Zero 2 W that turns a camera into an intelligent, network-accessible device built for agentic AI workflows.

EyeOfTheTiger runs an HTTP camera server and a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server, letting AI assistants like Claude capture images, describe scenes, detect motion, and trigger actions — all from your local network.

## What's Here

| Guide | Description |
|---|---|
| [Integrate with Anthropic](how-to/integrate-with-anthropic.md) | Connect EyeOfTheTiger to Claude via Claude Code or Claude Desktop |
| [Integrate with OpenAI](how-to/integrate-with-openai.md) | Use EyeOfTheTiger with OpenAI models |
| [Integrate with Google](how-to/integrate-with-google.md) | Connect to Google AI tools |
| [Integrate with Ollama](how-to/integrate-with-ollama.md) | Run local models against your camera feed |
| [Integrate with OpenClaw](how-to/integrate-with-openclaw.md) | Use EyeOfTheTiger through the OpenClaw platform |

## Getting Started

Before following any integration guide, make sure your EyeOfTheTiger device is set up and on your network. Once it is, the API and MCP server will be available at:

```text
http://eyeofthetiger.local/
```

You can verify it's running by visiting:

```text
http://eyeofthetiger.local/docs
```

For device setup instructions, see the [webcam-server-rp](https://github.com/eyeofthetiger-ai/webcam-server-rp) repository.

## Examples

Looking for ready-to-run projects built on EyeOfTheTiger? Check out the [examples](https://github.com/eyeofthetiger-ai/examples) repository, which includes projects like motion detection, daily timelapse, and person-spotted notifications.
