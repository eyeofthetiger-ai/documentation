# Link EyeOfTheTiger With Ollama

This file explains how to use EyeOfTheTiger with Ollama through OpenClaw.

Ollama lets you run open source models locally. OpenClaw provides the local
gateway and dashboard that connects those models to EyeOfTheTiger's Model
Context Protocol (MCP) server.

## Setting up the EyeOfTheTiger

You should follow the EyeOfTheTiger setup instructions to get it onto your
network.

EyeOfTheTiger exposes a Model Context Protocol (MCP) server at:

```text
http://eyeofthetiger.local/mcp/
```

After you have followed the steps, you can check the API and MCP server are up
by running:

```bash
manual_check/ping.sh
```

## Setting up Ollama

Go to the Ollama website, install Ollama, and choose the model you want to use:

- Ollama website: https://ollama.com/

Then launch OpenClaw with your chosen Ollama model:

```bash
ollama launch openclaw <model>
```

Replace `<model>` with the model you want to run.

## Configure the MCP server

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

Restart the OpenClaw gateway:

```bash
openclaw gateway restart
```

Navigate to the OpenClaw dashboard at http://127.0.0.1:18789/ or
http://localhost:18789/.

Start a new chat and run this test prompt:

```text
Using eyeofthetiger mcp server, tell me what you see.
```

OpenClaw should use the `eyeofthetiger` MCP server to capture an image from the
camera and describe it using your local Ollama model.
