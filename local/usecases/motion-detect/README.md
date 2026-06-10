# Motion Detection Event Recorder

A motion detection project that polls the EyeOfTheTiger still-image endpoint
and records short video clips when something changes in view.

We have included the code created by pasting the instructions below into Claude
Code in the [`app/`](app/) folder.

## How it works

1. A Python application polls `GET http://eyeofthetiger.local/v1/image` at a
   configurable interval to fetch still JPEG frames from the camera.
2. Each new frame is compared to the previous one using OpenCV.
3. When the changed area exceeds a configurable threshold, the app saves the
   two compared frames and a visual diff image.
4. The app then starts a device-side recording via `POST /v1/start`, waits the
   configured duration, stops it via `POST /v1/stop`, and downloads the
   finished H.264 MP4 from `GET /v1/recording`.
5. A small local web interface lists detected events and lets you inspect the
   initial frame, second frame, diff, and recorded video.

## What you need

- EyeOfTheTiger running and reachable on your network.
- Python 3 installed on the client computer that will monitor the camera.

## Architecture

```text
EyeOfTheTiger
    <- GET http://eyeofthetiger.local/v1/image  (polled on interval)
    -> client-side Python app
        -> OpenCV compares successive frames
        -> changed area exceeds threshold
        -> save initial.jpg, second.jpg, diff.jpg
        -> POST http://eyeofthetiger.local/v1/start
        -> wait record_seconds
        -> POST http://eyeofthetiger.local/v1/stop
        -> GET  http://eyeofthetiger.local/v1/recording  (download event.mp4)
        -> save event metadata in output/events/<timestamp>/

browser
    -> local event-review web app
        -> event list
        -> initial frame, second frame, diff, and video
```

## Building it with an AI agent

Paste the following prompt into your agent, for example Claude Code, to have it
create the project for you:

```text
Build a client-side motion detection event recorder in this directory. Use the
EyeOfTheTiger still-image endpoint:

  GET http://eyeofthetiger.local/v1/image

Poll it at a configurable interval to fetch frames. Do not modify the
EyeOfTheTiger server. The app must run on this client computer.

For recording clips after motion is detected, use the EyeOfTheTiger recording
API (all calls made from this client):

  POST http://eyeofthetiger.local/v1/start   — start recording on the device
  POST http://eyeofthetiger.local/v1/stop    — stop recording and finalise
  GET  http://eyeofthetiger.local/v1/recording — download the finished MP4

Build the project in two stages. Follow each stage exactly. Do not start stage
2 until I confirm stage 1 is working.

---

STAGE 1 - Create and test the motion detector

1. Create an app folder. Put all application code, templates, and
   requirements.txt inside app/. Create a Python virtual environment called
   .venv alongside app/. Use OpenCV for image processing and requests for HTTP
   calls.

2. Create an output/events folder. Each detected event must be stored in its
   own timestamped folder:

   output/events/YYYY-MM-DD_HH-MM-SS/

3. Create app/detector.py. It must:
   - Fetch frames by polling GET http://eyeofthetiger.local/v1/image using
     requests. Decode each response with cv2.imdecode.
   - Retry after a short delay if a fetch fails.
   - Compare each new frame to the previous one. Downscale, convert to
     greyscale, and blur both frames before comparing.
   - Use cv2.absdiff to create a visual difference image.
   - Calculate the proportion of pixels which differ by more than a
     configurable pixel threshold.
   - Trigger an event when that changed proportion exceeds a configurable
     changed-area threshold.
   - Add a configurable cooldown so one movement does not create many events.
   - When motion is detected, save:
       initial.jpg - the previous frame used in the comparison
       second.jpg  - the current frame used in the comparison
       diff.jpg    - a clear visual representation of the changed pixels
       event.json  - timestamp, thresholds, calculated score, poll interval,
                     record seconds, and file names
   - After saving frames, record a clip using the EyeOfTheTiger recording API:
       POST /v1/start to start recording on the device
       Wait --record-seconds seconds
       POST /v1/stop to finalise the clip
       GET  /v1/recording to download the MP4, save it as event.mp4
   - Make polling interval a command-line option called --poll-interval
     (default: 1.0 seconds).
   - Make clip duration a command-line option called --record-seconds
     (default: 10 seconds).
   - Keep monitoring after each event until I stop it with Ctrl-C.
   - Print clear status messages when fetching, detecting motion, recording,
     downloading, and shutting down.

4. Give me the exact commands to install dependencies and run app/detector.py.

5. Run app/detector.py and ask me to move in front of the camera. Wait for me to
   confirm that an event folder has been created. Then inspect the folder and
   open initial.jpg, second.jpg, and diff.jpg so I can confirm the detection
   looks reasonable.

6. Ask me: "Do the captured frames and diff look correct? Should I proceed to
   build the event browser?"

Wait for my answer before continuing.

---

STAGE 2 - Build the event browser (only if I said yes above)

1. Create app/app.py and any required HTML, CSS, and JavaScript files under
   app/ for a simple local web interface.

2. The interface must:
   - List detected events newest first with their timestamp and motion score.
   - Let me select an event.
   - Show the selected event's initial.jpg, second.jpg, and diff.jpg side by
     side with clear labels.
   - Show the selected event's event.mp4 in a video player with playback
     controls.
   - Handle the empty state when no events have been recorded.
   - Read event folders from output/events rather than requiring a database.
   - Serve saved images and videos through the application.
   - Use a clean, compact layout that works on desktop and mobile screens.

3. Add a short README section containing:
   - setup commands
   - the command to run app/detector.py
   - the command to run the event browser
   - the local URL for the browser
   - a note explaining the --poll-interval, --record-seconds, pixel threshold,
     changed-area threshold, and cooldown options

4. Run the browser locally and open it for me. Verify that the test event is
   listed and that the three images and video can be viewed.
```

## Setup and usage

```bash
# 1. Create the virtual environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install -r app/requirements.txt

# 2. Run the motion detector
.venv/bin/python app/detector.py

# 3. Run the event browser (in a separate terminal)
.venv/bin/python app/app.py
```

Open the event browser at: **http://localhost:5000**

### app/detector.py options

| Flag | Default | Description |
|------|---------|-------------|
| `--poll-interval N` | 1.0 | Seconds between image fetches. Increase to reduce camera load; decrease to catch faster motion. |
| `--record-seconds N` | 10 | Duration in seconds to record on the device after motion is detected. |
| `--pixel-threshold N` | 25 | Per-pixel absolute difference that counts as "changed". Increase to ignore compression noise. |
| `--changed-area-threshold F` | 0.02 | Proportion of pixels (0–1) that must change to trigger an event. Increase to reduce false positives from leaves or lighting shifts. |
| `--cooldown N` | 15 | Seconds to suppress further events after one fires. Prevents a single continuous movement from filling the event log. |

## Tuning

Motion detection needs a little tuning for the scene. A shorter poll interval
makes faster movements detectable but increases load on the camera. A higher
changed-area threshold reduces false positives from small changes such as
leaves moving or camera noise. A cooldown keeps one continuous movement from
producing a large number of clips.
