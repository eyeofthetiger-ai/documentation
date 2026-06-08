# Link EyeOfTheTiger With Anthropic

There are three ways to connect EyeOfTheTiger to Anthropic tools.

## Option 1: Through OpenClaw

Follow the OpenClaw integration guide:

- [Link EyeOfTheTiger With OpenClaw](link-to-openclaw.md)

## Option 2: Through Claude Desktop

Claude Desktop integration is pending testing at the moment.

## Option 3: Through Claude Code

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
