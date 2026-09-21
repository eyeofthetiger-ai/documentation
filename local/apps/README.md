# Apps: run your own code on the EOT-1 or in the cloud

An app is a long-running program scoped to one camera. When running
on-device, your EOT-1 builds and runs it as a Docker container, watching the
live stream frame by frame, starting and stopping continuous recording, and
reporting structured events back, all with no network hop. In the cloud, the
platform `CloudAppRunner` creates a dedicated Cloud Run service for each
`(cameraId, appName)` pair that does the same work from the portal side. A
single camera can have some apps on-device and others in the cloud, and
catalog entries with `deployment_target: "both"` let you pick per install.

This is different from the [use cases](../usecases/README.md) in this repo: a
use case is a client-side script that runs on a separate computer and polls
your EOT-1's HTTP API from outside. An on-device app runs *on* the EOT-1; a
cloud app runs next to the gateway and polls the portal for that camera's
live-stream state. Reach for an app when you want continuous, low-latency
processing of the live stream, or when the processing needs to keep running
even when no other computer is around.

Before you start, make sure your EOT-1 is set up and on your network.
You can verify it's reachable by visiting `http://eyeofthetiger.local/docs` in
a browser, that's also where the full, field-by-field API reference lives.
Cloud callers use `https://platform.eyeofthetiger.ai/api/docs` instead.

## The contract

Every app is a Docker image (on-device: built by the EOT-1 itself; in the
cloud: pulled from GHCR) with a small fixed contract:

- **Must expose `GET /status`**: a liveness check plus whatever JSON your app
  wants to report. Your EOT-1 (or Cloud Run service) never interprets it,
  just relays it to the Apps page / portal.
- **May expose `POST /start` / `POST /stop`** for a soft pause and resume
  (e.g. keep in-memory state across a pause). On-device the server tries these
  first and falls back to a hard `docker start`/`docker stop` if your app
  doesn't implement them. In the cloud `start`/`stop` toggle Cloud Run
  scaling to `min=1/max=1` vs `0/0`.
- **On-device runs with `--network host`**, so it reaches the capture server on
  `localhost` and exposes its own port directly on the EOT-1's address. No
  per-app networking to configure. Cloud apps get `CAMERA_API_URL` /
  `CAMERA_API_KEY` / `CAMERA_ID` + `GCS_BUCKET`/`GCS_PREFIX` injected instead
  and poll the portal.
- **Resources**: on-device is a fixed 256 MB cap, not configurable. Cloud is
  `resource_profile: "cpu-small"` (2 vCPU / 4 GiB). The `gpu-l4` profile is
  not yet configured, and the portal rejects it until GPU quota is provisioned.
- **Dynamic controls for free**: tag an operation `"Controls"` in your own
  FastAPI/OpenAPI spec and it shows up as a button or form on the EOT-1's
  (or portal's) Apps page automatically, re-checked on every call, so this can
  never become an open proxy into your app.
- **Storage**: on-device uses named volumes at `/data/<name>`, kept across
  reinstall. Cloud install records (Firestore
  `cloud_app_installs/<cameraId>/apps/<name>`) keep only
  `name/imageRef/resourceProfile/status/error`.
- **Deployment target**: catalog entries carry
  `deployment_target: "device" | "cloud" | "both"`. Every cloud app today
  runs under the project `firebase-adminsdk-fbsvc` service account. There is
  no per-camera Workload Identity scoping yet.

## Install, manage, and monitor

| Method | Path                       | Description                                            |
|--------|----------------------------|----------------------------------------------------------|
| POST   | `/v1/apps`                 | On-device: install from a manifest + build-context tarball. Cloud: install from a catalog entry (same `POST`, the gateway dispatches by `(cameraId, name)`). |
| GET    | `/v1/apps`                 | List installed apps with live status (`deployment_target` tells you where each one runs) |
| GET    | `/v1/apps/{name}`          | One app's status plus its dynamic controls              |
| POST   | `/v1/apps/{name}/start`    | Start an app (on-device: soft → Docker-level; cloud: `1/1` scaling) |
| POST   | `/v1/apps/{name}/stop`     | Stop an app (on-device: soft → Docker-level; cloud: `0/0`) |
| GET    | `/v1/apps/{name}/logs`     | Stream the app's container logs                         |
| DELETE | `/v1/apps/{name}`          | Uninstall an app (on-device volume data is kept)         |

On-device manifest is `{"name", "port", "command", "env", "volumes"}`; `name`
and `port` are required, the rest are optional. Cloud catalog entry is
`{"name", "imageRef", "resourceProfile", "env?"}` (currently only
`resource_profile: "cpu-small"` is deployable). See
`http://eyeofthetiger.local/docs` and
`https://platform.eyeofthetiger.ai/api/docs` for the full validation rules.

## Events: telemetry your app reports

Alongside the apps platform, your EOT-1 runs a small local events store for
structured telemetry ("driver was drowsy from T1 to T2, here are the
metrics") that your app reports and your EOT-1 durably queues for upload.
An event is opaque JSON as far as your EOT-1 is concerned: it never
validates `type` or `payload` beyond a size limit, so you're free to define
your own event types.

What your EOT-1 does do is match every event, at the moment it's recorded,
to whichever continuous-recording segment covers its `started_at` timestamp,
so a human reviewing events later can click straight through to that
moment in the footage. Browse events on your EOT-1 itself at
`http://eyeofthetiger.local/events-log`.

| Method | Path         | Description                                                         |
|--------|--------------|----------------------------------------------------------------------|
| POST   | `/v1/events` | Report an event: `type`, `started_at`, `ended_at`, `payload`       |
| GET    | `/v1/events` | List events, filterable by type and date                            |

## Try it: a minimal example

[`test-app`](test-app/) is the smallest possible app: no camera or
computer-vision work at all, just timed calls into your EOT-1's own local
API. Every 60 seconds it:

1. `POST`s `/continuous-recording/start`
2. waits 10 seconds
3. `POST`s `/continuous-recording/stop`
4. `POST`s `/events` with `type: "test-app.tick"`, timestamped to a moment
   during the segment it just recorded
5. idles for the rest of the minute, then repeats

It exists purely to exercise the apps platform, continuous recording, and
the events API end to end, and it's a good starting skeleton for a real app
of your own: clone [`test-app/`](test-app/), keep the `/status` and
`Dockerfile` scaffolding, and swap the timer loop for whatever your app
actually needs to do. See [`test-app/README.md`](test-app/README.md) for
the install command.

Behind the scenes, this same platform also runs real computer-vision apps,
for example a driver-drowsiness detector that reads the live stream
continuously and reports drowsiness events the same way `test-app` reports
its ticks.

## Ideas for apps to build

Because an app runs on the EOT-1 itself, it fits best when you want
continuous, low-latency processing of the live stream with no separate
computer required:

- **Attention / drowsiness monitor**: watch the live stream continuously
  and flag when a driver or operator looks fatigued or distracted.
- **Package or parcel detector**: watch a porch or loading dock
  frame-by-frame and declare an event the moment a box appears, without
  round-tripping frames off the EOT-1.
- **Pet or wildlife activity logger**: run a small on-device classifier
  against the stream and log each sighting as an event with a species label
  and confidence score.
- **Workshop or kitchen safety monitor**: check continuously for a stove
  left on, smoke, or missing PPE, and raise an event the instant something
  looks wrong.
- **Nightly self-test**: on a timer, start continuous recording, stop it,
  and declare a "device healthy" event each morning, a lightweight watchdog
  for the recording pipeline itself. `test-app` above is exactly this
  pattern, just faster.

## See also

- [`test-app/`](test-app/): the full source for the minimal example above.
- [Use Cases](../usecases/README.md): client-side projects that run on a
  separate computer and poll your EOT-1's API from outside.
- `http://eyeofthetiger.local/docs`: the full, interactive API reference
  served by your EOT-1, including the complete apps and events schemas.
