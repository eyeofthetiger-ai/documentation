# test-app

A minimal on-device app for exercising the capture server's apps platform,
continuous recording, and events API end to end — no camera or computer
vision work at all, just timed HTTP calls into the capture server's own
local API. See the [Apps guide](../README.md) for how the platform itself
works.

## What it does

Every 60 seconds:
1. `POST /continuous-recording/start`
2. wait 10s
3. `POST /continuous-recording/stop`
4. `POST /events` with `type: "test-app.tick"`, timestamped to a moment
   during the just-recorded segment
5. idle for the rest of the minute, repeat

The event is declared *after* stopping, not before: the capture server's
continuous-recording `stop()` blocks until the just-finished segment is
fully closed and written to its durable index, so by the time this app
POSTs the event, the capture server can already match it against that
segment — every event this app produces gets a real `recording_id`/
`offset_s` instead of `null`.

## Install it

From the device's Apps page (`http://eyeofthetiger.local/apps-page`) or via
the API:

```bash
tar -czf test-app-context.tar.gz -C test-app service.py requirements.txt Dockerfile .dockerignore

curl -X POST http://eyeofthetiger.local/v1/apps \
  -F 'manifest={"name":"test-app","port":8101,"command":["python","service.py","--capture-url","http://127.0.0.1:80","--port","8101"]}' \
  -F 'context=@test-app-context.tar.gz'
```

## Check it

```bash
curl http://eyeofthetiger.local:8101/status
```
