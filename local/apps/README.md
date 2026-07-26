# Apps: run your own code on the device

An app is a long-running program that the camera builds and runs for you, on
its own hardware — not on a separate computer. It can watch the live stream
frame by frame, start and stop continuous recording, and report structured
events back to the device, all with no network hop to a laptop or server.

This is different from the [use cases](../usecases/README.md) in this repo: a
use case is a client-side script that runs on a separate computer and polls
the camera's HTTP API from outside. An app runs on the camera itself. Reach
for an app when you want continuous, low-latency processing of the live
stream, or when the processing needs to keep running even when no other
computer is around.

Before you start, make sure your EyeOfTheTiger is set up and on your network.
You can verify it's reachable by visiting `http://eyeofthetiger.local/docs` in
a browser — that's also where the full, field-by-field API reference for
everything below lives.

## The contract

Every app is a Docker image, built and run by the device itself, with a small
fixed contract:

- **Must expose `GET /status`** — a liveness check plus whatever JSON your app
  wants to report. The device never interprets it, just relays it as-is to
  the Apps page.
- **May expose `POST /start` / `POST /stop`** for a soft pause and resume
  (e.g. keep in-memory state across a pause). The device tries these first
  and falls back to a hard `docker start`/`docker stop` if your app doesn't
  implement them, or its HTTP server has hung — so lifecycle control always
  works even if your app is broken.
- **Runs with `--network host`**, so it reaches the capture server on
  `localhost` and exposes its own port directly on the device's address. No
  per-app networking to configure.
- **Gets a fixed 256 MB memory cap**, not configurable. This is a 1 GB Pi,
  and a runaway app must not be able to starve the camera service itself.
- **Dynamic controls for free**: tag an operation `"Controls"` in your own
  FastAPI/OpenAPI spec and it shows up as a button or form on the device's
  Apps page automatically — re-checked on every call, so this can never
  become an open proxy into your app.
- **Named volumes, not host paths**: declare logical volume names in your
  manifest and the device gives each one a directory that survives
  uninstall/reinstall, mounted at a fixed `/data/<name>` path inside your
  container. You never specify a host path yourself.

## Install, manage, and monitor

Install from the device's Apps page (`http://eyeofthetiger.local/apps-page`)
or straight over the API. Installing is a source upload, not a registry pull:
you send a small JSON manifest plus a build-context tarball (a `Dockerfile`
and whatever source it needs), and the device `docker build`s it natively on
its own architecture — no cross-compilation step required on your end.

| Method | Path                       | Description                                            |
|--------|----------------------------|----------------------------------------------------------|
| POST   | `/v1/apps`                 | Install an app from a manifest + build-context tarball |
| GET    | `/v1/apps`                 | List installed apps with live status                   |
| GET    | `/v1/apps/{name}`          | One app's status plus its dynamic controls              |
| POST   | `/v1/apps/{name}/start`    | Start an app (soft, falling back to Docker-level)       |
| POST   | `/v1/apps/{name}/stop`     | Stop an app (soft, falling back to Docker-level)        |
| GET    | `/v1/apps/{name}/logs`     | Stream the app's container logs                         |
| DELETE | `/v1/apps/{name}`          | Uninstall an app (its volume data is kept)               |

The manifest is `{"name", "port", "command", "env", "volumes"}` — `name` and
`port` are required, the rest are optional. See
`http://eyeofthetiger.local/docs` for the full validation rules on each
field.

## Events: telemetry your app reports

Alongside the apps platform, the device runs a small local events store for
structured telemetry — "driver was drowsy from T1 to T2, here are the
metrics" — that your app reports and the device durably queues for upload.
An event is opaque JSON as far as the device is concerned: it never
validates `type` or `payload` beyond a size limit, so you're free to define
your own event types.

What the device does do is match every event, at the moment it's recorded,
to whichever continuous-recording segment covers its `started_at` timestamp
— so a human reviewing events later can click straight through to that
moment in the footage. Browse events on the device itself at
`http://eyeofthetiger.local/events-log`.

| Method | Path         | Description                                                         |
|--------|--------------|----------------------------------------------------------------------|
| POST   | `/v1/events` | Report an event: `type`, `started_at`, `ended_at`, `payload`       |
| GET    | `/v1/events` | List events, filterable by type and date                            |

## Try it: a minimal example

[`test-app`](test-app/) is the smallest possible app — no camera or
computer-vision work at all, just timed calls into the device's own local
API. Every 60 seconds it:

1. `POST`s `/continuous-recording/start`
2. waits 10 seconds
3. `POST`s `/continuous-recording/stop`
4. `POST`s `/events` with `type: "test-app.tick"`, timestamped to a moment
   during the segment it just recorded
5. idles for the rest of the minute, then repeats

It exists purely to exercise the apps platform, continuous recording, and
the events API end to end, and it's a good starting skeleton for a real app
of your own — clone [`test-app/`](test-app/), keep the `/status` and
`Dockerfile` scaffolding, and swap the timer loop for whatever your app
actually needs to do. See [`test-app/README.md`](test-app/README.md) for
the install command.

Behind the scenes, this same platform also runs real computer-vision apps
— for example, a driver-drowsiness detector that reads the live stream
continuously and reports drowsiness events the same way `test-app` reports
its ticks.

## Ideas for apps to build

Because an app runs on the device itself, it fits best when you want
continuous, low-latency processing of the live stream with no separate
computer required:

- **Attention / drowsiness monitor** — watch the live stream continuously
  and flag when a driver or operator looks fatigued or distracted.
- **Package or parcel detector** — watch a porch or loading dock
  frame-by-frame and declare an event the moment a box appears, without
  round-tripping frames off the device.
- **Pet or wildlife activity logger** — run a small on-device classifier
  against the stream and log each sighting as an event with a species label
  and confidence score.
- **Workshop or kitchen safety monitor** — check continuously for a stove
  left on, smoke, or missing PPE, and raise an event the instant something
  looks wrong.
- **Nightly self-test** — on a timer, start continuous recording, stop it,
  and declare a "device healthy" event each morning, a lightweight watchdog
  for the recording pipeline itself. `test-app` above is exactly this
  pattern, just faster.

## See also

- [`test-app/`](test-app/) — the full source for the minimal example above.
- [Use Cases](../usecases/README.md) — client-side projects that run on a
  separate computer and poll the camera's API from outside.
- `http://eyeofthetiger.local/docs` — the full, interactive API reference
  served by your device, including the complete apps and events schemas.
