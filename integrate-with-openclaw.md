# Link EyeOfTheTiger With OpenClaw

This file explains how to link your EyeOfTheTiger device
with OpenClaw.

OpenClaw is a local AI gateway and dashboard that can connect AI models to
tools exposed over Model Context Protocol (MCP). In this setup, it lets an AI
chat use the EyeOfTheTiger camera through the device's MCP server.

OpenClaw enables integration with all major AI providers,
including OpenAI, Google, and Anthropic, as well as open source locally hosted
models, for example through Ollama.

## Setting up the EyeOfTheTiger

You should follow the EyeOfTheTiger setup instructions to get it onto your network.

EyeOfTheTiger exposes a Model Context Protocol (MCP) server at:

```text
http://eyeofthetiger.local/mcp/
```

After you have followed the steps, you can check the API and MCP server are up
by running:

```bash
manual_check/ping.sh
```

## Setting up OpenClaw

See the OpenClaw website and docs:

- OpenClaw website: https://www.openclaw.org/
- OpenClaw MCP docs: https://docs.openclaw.ai/cli/mcp

## Integration

Add the EyeOfTheTiger to OpenClaw with:

```bash
openclaw mcp set eyeofthetiger '{"url":"http://eyeofthetiger.local/mcp/","transport":"streamable-http"}'
```

You can list all configured MCP servers with:

```bash
openclaw mcp list
```

You should see `eyeofthetiger` on the list.

## Run a test

Restart the openclaw gateway:

```bash
openclaw gateway restart
```

Navigate to the openclaw dashboard at http://127.0.0.1:18789/ (or http://localhost:18789/)

Start a new chat and ask the agent to check the configured MCP servers:

```text
Run the command-line command `openclaw mcp list` and tell me whether the
eyeofthetiger MCP server is configured.
```

Check that the agent runs the command and correctly identifies `eyeofthetiger`
in the output. Then ask it to use the camera:

```text
Using the eyeofthetiger MCP server, tell me what you see.
```

OpenClaw should use the `eyeofthetiger` MCP server to capture an image from the
camera and describe it. The first time it is run it will likely take a while
setting up the infrastructure it needs to do image processing, and finding out
what tools are available via the mcp server but subsequent calls will be much
quicker.

If it says the server cannot be reached, confirm that
the EyeOfTheTiger is powered on, connected to the same Wi-Fi network, and still
listed by `openclaw mcp list`.
