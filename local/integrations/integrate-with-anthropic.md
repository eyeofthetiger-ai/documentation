# Link EyeOfTheTiger With Anthropic

There are three ways to connect EyeOfTheTiger to Anthropic tools.

Before you start, make sure your EyeOfTheTiger is set up and on your network.
You can verify it's reachable by visiting `http://eyeofthetiger.local/docs` in
a browser.

## Option 1: Through Claude Code

EyeOfTheTiger exposes a Model Context Protocol (MCP) server at:

```text
http://eyeofthetiger.local/mcp/
```

Add the EyeOfTheTiger to Claude Code with:

```bash
claude mcp add --transport http eyeofthetiger http://eyeofthetiger.local/mcp/
```

Start Claude Code and run this test prompt:

```text
Using eyeofthetiger mcp server, tell me what you see.
```

Claude Code should use the `eyeofthetiger` MCP server to capture an image from
the camera and describe it.

## Option 2: Through Claude Desktop

Claude Desktop integration is pending testing at the moment.

## Option 3: Through OpenClaw

Follow the OpenClaw integration guide:

- [Link EyeOfTheTiger With OpenClaw](integrate-with-openclaw.md)
