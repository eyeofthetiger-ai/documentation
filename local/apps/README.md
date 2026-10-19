# Apps

An app gives your EOT-1 a job and keeps doing it: watching the live stream,
taking snapshots, starting and stopping recordings, and reporting what it
finds. Once installed it runs on its own, so you don't need to keep a
computer switched on or a script running.

Looking to install a ready-made app, or publish your own for other EOT-1
owners? See the [Marketplace guide](../../cloud/marketplace.md): step-by-step
install, credits, and submitting an app.

## What an app can do

An app uses the same API you can call yourself, so anything you can do with
your EOT-1, an app can do for you, continuously:

- read the live stream and take snapshots,
- start and stop continuous video and audio recording,
- record events, each linked to the moment in the footage it happened
  (on-device apps),
- serve its own web page, for a dashboard or live view,
- add its own buttons and forms to the portal (on-device apps).

## Where an app runs

Every app runs in one of two places, and an EOT-1 can have both kinds
installed at once.

| | On your EOT-1 | In the cloud |
|---|---|---|
| **What it is** | A Docker container on your EOT-1 | A Cloud Run service that EyeOfTheTiger hosts, one per EOT-1 and app |
| **How it reaches your EOT-1** | Directly at `http://127.0.0.1`: every frame of the live stream, no network hop | Over the internet, through the platform API (`CAMERA_API_URL` + `CAMERA_API_KEY`) |
| **Resources** | 256 MB memory and 2 CPU cores, fixed | `cpu-tiny` (1 vCPU, 512 MiB), `cpu-small` (2 vCPU, 4 GiB) or `gpu-l4` (4 vCPU, 16 GiB, NVIDIA L4 GPU) |
| **Cost to run** | Free: it uses your EOT-1 | Charged per hour from your [credits](../../cloud/marketplace.md#credits-how-apps-are-paid-for) while it runs |
| **Storage** | Named volumes at `/data/<name>`, kept when the app is deleted or reinstalled | None: its disk is wiped whenever it stops |
| **Reports events** | Yes, with `POST /v1/events` | Not yet |
| **Its own buttons and forms** | Yes (dynamic controls) | Not yet |
| **Its own web page** | At `http://eyeofthetiger.local:<port>` on your network | Opened from the portal with **Open** |
| **Where it comes from** | The Marketplace, or your own code installed over your local network | The Marketplace only: EyeOfTheTiger's apps and apps people have published |

**Run it on your EOT-1** for continuous, lightweight work on every frame:
detectors, loggers and watchdogs that should keep going even when your
internet connection drops. Events are queued on the EOT-1 and uploaded when
it's back online.

**Run it in the cloud** when the work needs more than the EOT-1 has: large
models, a GPU, or several GiB of memory. A cloud app needs your EOT-1 online
and your credits above £0.

Some apps use both. A **bundle** installs several apps together, for example
a small on-device app that watches for motion and starts a cloud app only
when there's something to analyse, then stops it again. You pay for the cloud
part only while it runs.

## Install and manage apps

Install apps from the [Marketplace](../../cloud/marketplace.md#install-an-app-from-the-marketplace)
in the portal. Each EOT-1's page in the portal lists its apps, wherever they
run, with **Start**, **Stop**, **Logs** and **Delete**. Cloud apps with their
own page also have **Open**. On-device apps also have **Download logs** and
**Custom controls**.

- **On-device apps need the apps platform switched on.** It runs Docker,
  which uses about 80 MB of the EOT-1's memory even with no apps, so you can
  switch it off when you don't use apps. The install form offers to switch
  it on. Switching it off stops every on-device app.
- **Stopping** an on-device app pauses its container. Stopping a cloud app
  shuts its service down, which stops the hourly charge.
- **Deleting** an on-device app keeps its volume data, so reinstalling it
  under the same name picks up where it left off. A cloud app keeps nothing.
- On your local network, `http://eyeofthetiger.local/apps-page` lists your
  on-device apps with their status, logs and controls.

## What every app must do

Wherever it runs, an app is a container that:

- serves HTTP on one port, between 1024 and 65535,
- answers `GET /status` with JSON about how it's doing. Your EOT-1 and the
  portal never interpret it; they show it as it is.

Each place adds a few rules of its own, below.

## Build an app that runs on your EOT-1

You upload your app's source (a `Dockerfile` and whatever it needs) and your
EOT-1 builds it with `docker build` on its own hardware, so there's nothing
to cross-compile. It runs with `--network host`: `http://127.0.0.1` inside
your app is your EOT-1's own API, and your app's port is open at
`http://eyeofthetiger.local:<port>`.

Every on-device app is capped at 256 MB of memory and 2 CPU cores, so a
runaway app can't starve the camera itself. The caps can't be changed.

### Optional extras

- **Soft start and stop.** Expose `POST /start` and `POST /stop` to pause and
  resume without losing in-memory state. Your EOT-1 tries these first and
  falls back to starting or stopping the container if they're missing or
  your app has hung.
- **Dynamic controls.** Tag an operation `"Controls"` in your app's OpenAPI
  spec (FastAPI does this with `tags=["Controls"]`) and it appears as a button
  or form under **Custom controls** in the portal and on your EOT-1's local
  Apps page. Your EOT-1 reads the spec fresh on every call and only forwards
  operations that are in it.

### The manifest

Installing an app takes a JSON manifest alongside the source tarball:

| Field | What it is |
|---|---|
| `name` | Required. Lowercase letters, digits and hyphens, up to 63 characters, starting with a letter or digit. Also the container name. |
| `port` | Required. The port your app serves HTTP on, 1024 to 65535. |
| `command` | Optional. Overrides the image's own `CMD`, as a list of strings. |
| `env` | Optional. Environment variables, as string to string. |
| `volumes` | Optional. A list of volume names (not paths). Each is mounted at `/data/<name>`. |
| `description` | Optional. Shown on the Apps page, up to 500 characters. |
| `triggers_cloud_apps` | Optional. Names of cloud apps on the same EOT-1 this app may start and stop (see [Waking a cloud app](#waking-a-cloud-app)). |

### Install it over your local network

From a computer on the same network as your EOT-1, pack the source and post
it with the manifest. Changes on your EOT-1's local API need the
`X-EOT-Local: 1` header.

```bash
tar -czf test-app-context.tar.gz -C test-app service.py requirements.txt Dockerfile .dockerignore

curl -X POST http://eyeofthetiger.local/v1/apps \
  -H 'X-EOT-Local: 1' \
  -F 'manifest={"name":"test-app","port":8101,"command":["python","service.py","--capture-url","http://127.0.0.1:80","--port","8101"]}' \
  -F 'context=@test-app-context.tar.gz'

curl http://eyeofthetiger.local:8101/status
```

Installs from the portal or the platform API only pull EyeOfTheTiger's own
published images, so your own on-device app is installed this way, over your
local network.

### Local apps API

| Method | Path | Description |
|---|---|---|
| POST | `/v1/apps` | Install an app from a manifest and a build-context tarball |
| GET | `/v1/apps` | List installed apps with their live status |
| GET | `/v1/apps/{name}` | One app's status and its dynamic controls |
| POST | `/v1/apps/{name}/start` | Start an app (its own `/start` first, then Docker) |
| POST | `/v1/apps/{name}/stop` | Stop an app (its own `/stop` first, then Docker) |
| POST | `/v1/apps/{name}/controls` | Call one of the app's dynamic controls |
| GET | `/v1/apps/{name}/logs` | Stream the app's logs (Server-Sent Events) |
| GET | `/v1/apps/{name}/logs/download` | Download the app's logs as a gzip file |
| DELETE | `/v1/apps/{name}` | Uninstall an app (its volume data is kept) |
| POST | `/v1/apps/{name}/cloud-apps/{cloud_app}/{action}` | Start or stop a cloud app this app declared |
| GET | `/v1/apps-platform/status` | Whether the apps platform is on |
| POST | `/v1/apps-platform/enable` | Switch the apps platform on |
| POST | `/v1/apps-platform/disable` | Switch it off, stopping every on-device app |

Full request and response shapes are in your EOT-1's own API docs at
`http://eyeofthetiger.local/docs`.

### Recording events

An event is a small JSON record of something your app noticed, like "driver
looked drowsy from T1 to T2, here are the metrics". Your EOT-1 stores it,
links it to the recording segment covering that moment, and uploads it to
the portal's **Events** page, where you can click through to the footage.
Your EOT-1 doesn't check `type` or `payload` beyond a size limit.

| Method | Path | Description |
|---|---|---|
| POST | `/v1/events` | Record an event: `type`, `started_at`, `ended_at`, `payload` |
| GET | `/v1/events` | List events, filtered by type and date |

Browse them on your EOT-1 at `http://eyeofthetiger.local/events-log`, or from
anywhere with `GET /api/v1/cameras/:id/events` on the platform API.

### Waking a cloud app

An on-device app can start and stop a cloud app on the same EOT-1, without
holding any portal credentials, by calling
`POST /v1/apps/{name}/cloud-apps/{cloud_app}/start` (or `/stop`). It can only
do this for cloud apps listed in its manifest's `triggers_cloud_apps`.

### Try it: a minimal example

[`test-app`](test-app/), installed by the commands above, is the smallest
useful app: no computer vision, just timed calls to your EOT-1's API. Every
60 seconds it starts continuous recording, waits 10 seconds, stops it, and
records one event linked to the segment it just recorded. It's a good
skeleton for an app of your own: keep the `/status` and `Dockerfile`
scaffolding and swap the timer loop for whatever your app needs to do.

## Build an app that runs in the cloud

EyeOfTheTiger builds cloud apps from your GitHub repository and runs them on
Google Cloud Run. To run one, submit it to the Marketplace: it's reviewed,
then listed for every EOT-1 owner. In short, your app:

- has a `Dockerfile` at the root of a public repository,
- reaches the EOT-1 it was installed for through the platform API, using the
  `CAMERA_API_URL`, `CAMERA_API_KEY` and `CAMERA_ID` environment variables
  the platform sets,
- keeps anything it needs to remember somewhere else, since its disk is
  wiped when it stops,
- checks the portal's token on every request if it serves its own page.

[Publish your own app](../../cloud/marketplace.md#publish-your-own-app) has
the full contract, a template to start from, pricing and the review process.

Not yet available for cloud apps: dynamic controls, recording events, and
running a private cloud app without publishing it.

## Ideas for apps to build

Most of these suit a lightweight on-device app; heavier models belong in the
cloud.

- **Attention / drowsiness monitor** (on-device): watch the live stream
  continuously and flag when a driver or operator looks fatigued or
  distracted.
- **Package or parcel detector** (on-device): watch a porch or loading dock
  frame by frame and record an event the moment a box appears, without
  anything leaving your EOT-1.
- **Pet or wildlife activity logger** (on-device): run a small classifier
  against the stream and log each sighting as an event with a species label
  and confidence score.
- **Workshop or kitchen safety monitor** (on-device): check continuously for
  a stove left on, smoke, or missing PPE, and record an event the instant
  something looks wrong.
- **Nightly self-test** (on-device): on a timer, start continuous recording,
  stop it, and record a "device healthy" event each morning. `test-app` above
  is exactly this pattern, just faster.
- **Heavy models on a GPU** (cloud, with an on-device trigger): run a model
  too big for the EOT-1, such as detailed sports or object tracking, on a
  cloud GPU. Pair it with a small on-device app that wakes it only when there
  is motion, so you only pay while something is happening.

## See also

- [Marketplace](../../cloud/marketplace.md): install apps, pay with credits,
  and publish your own cloud app.
- [`test-app/`](test-app/): the full source for the minimal example above.
- [Use cases](../usecases/README.md): if you'd rather run your own code on
  your laptop or server and call your EOT-1 from there.
- `http://eyeofthetiger.local/docs`: the full, interactive API reference
  served by your EOT-1.
