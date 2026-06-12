# Kitchen Assistant

Use EyeOfTheTiger with OpenClaw as a conversational kitchen assistant. Point
the camera at your worktop, then ask your AI model to take a fresh look when
you want a visual check:

```text
Using the eyeofthetiger camera, check whether the bread is browned enough.
```

The model can call the camera's MCP `take_snapshot` tool, inspect the returned
JPEG, and answer in the context of your conversation. You can ask follow-up
questions such as:

```text
Check again. Has it changed enough since the last photo?
```

## Why use MCP?

The other examples use the HTTP API or MJPEG stream for predetermined tasks
such as taking a photo every two minutes or continuously detecting motion.
This example is different: your AI model decides when to use the camera while
helping you with an open-ended task.

EyeOfTheTiger exposes three MCP tools:

- `take_snapshot`: take a fresh JPEG image.
- `get_configuration`: inspect the current capture resolution.
- `set_configuration`: change the capture resolution.

## How the connection works

EyeOfTheTiger runs its MCP server on your local network:

```text
http://eyeofthetiger.local/mcp/
```

OpenClaw runs locally and connects directly to that MCP server:

```text
OpenClaw dashboard
    -> local OpenClaw gateway
    -> local network: http://eyeofthetiger.local/mcp/
    -> EyeOfTheTiger camera
```

The camera's MCP endpoint uses plain HTTP without authentication. Keep
EyeOfTheTiger and OpenClaw on a trusted private network. Do not expose the MCP
endpoint to the public internet.

## Prerequisites

- An EyeOfTheTiger camera that has completed the [main setup](../../README.md)
  and is connected to the same local network as your computer.
- [OpenClaw](https://www.openclaw.org/) installed and configured with the AI
  model you want to use.

OpenClaw supports major AI providers such as Anthropic, Google, and OpenAI. It
can also use a locally hosted model through Ollama. See the
[OpenClaw integration guide](../../integrations/integrate-with-openclaw.md) and
[Ollama integration guide](../../integrations/integrate-with-ollama.md) for the
general setup paths.

## Set up OpenClaw

### 1. Check the camera server

From this repository, run:

```bash
manual_check/ping.sh
```

The command should report that the HTTP API responded and list the available
MCP tools.

### 2. Add the MCP server to OpenClaw

Register the EyeOfTheTiger MCP server:

```bash
openclaw mcp set eyeofthetiger '{"url":"http://eyeofthetiger.local/mcp/","transport":"streamable-http"}'
```

Check the saved MCP server list:

```bash
openclaw mcp list
```

You should see `eyeofthetiger` in the output.

### 3. Restart the OpenClaw gateway

Apply the updated configuration:

```bash
openclaw gateway restart
```

Open the dashboard:

```bash
openclaw dashboard
```

The local dashboard is normally available at:

```text
http://127.0.0.1:18789/
```

### 4. Ask your model to look at the worktop

Place something in view of the camera and start a new chat. First ask the agent
to check the configured MCP servers:

```text
Run the command-line command `openclaw mcp list` and tell me whether the
eyeofthetiger MCP server is configured.
```

Check that the agent runs the command and correctly identifies `eyeofthetiger`
in the output. Then ask it to use the camera:

```text
Using the eyeofthetiger camera, tell me what you see on the worktop.
```

The model should call `take_snapshot` and describe the image. Keep the
conversation going with questions such as:

```text
Does the dough look smooth enough to shape?
```

```text
Check the camera again. Are the cookies starting to brown at the edges?
```

```text
Look at the worktop and tell me whether I have all the ingredients laid out.
```

## Troubleshooting

If the tools do not appear:

1. Run `manual_check/ping.sh` again to confirm that the Pi is reachable.
2. Run `openclaw mcp list` and confirm that `eyeofthetiger` is present.
3. Inspect the saved definition:

   ```bash
   openclaw mcp show eyeofthetiger --json
   ```

4. Restart the gateway with `openclaw gateway restart`.
5. Confirm that your OpenClaw host and EyeOfTheTiger are connected to the same
   local network.

The `openclaw mcp set` command saves the server definition but does not test
the live connection. Use `manual_check/ping.sh` when you need to verify that
the camera server is responding.

If `openclaw gateway restart` fails, inspect the gateway status and service
logs:

```bash
openclaw status
journalctl --user -u openclaw-gateway.service -n 200 --no-pager
```

The failure may come from an existing OpenClaw integration rather than the
EyeOfTheTiger MCP server. Resolve the reported OpenClaw configuration error,
then retry `openclaw gateway restart`.

## Further reading

- [Link EyeOfTheTiger With OpenClaw](../../integrations/integrate-with-openclaw.md)
- [OpenClaw MCP documentation](https://docs.openclaw.ai/cli/mcp)
- [OpenClaw dashboard documentation](https://docs.openclaw.ai/web/dashboard)
