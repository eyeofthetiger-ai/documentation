# Motion Detection Event Recorder

A motion detection project that watches the EyeOfTheTiger MJPEG
stream and records short video clips when something changes in view. 

We have included the code created by pasting the instructions below into Claude
Code in the [`app/`](app/) folder.

## How it works

1. A Python application opens the EyeOfTheTiger MJPEG stream at
   `http://eyeofthetiger.local/stream.mjpg`.
2. OpenCV samples the stream and compares frames a configurable number of
   frames apart.
3. When the changed area exceeds a configurable threshold, the app saves the
   two compared frames, a visual diff image, and the following few seconds of
   video.
4. A small local web interface lists detected events and lets you inspect the
   initial frame, second frame, diff, and recorded video.

## What you need

- EyeOfTheTiger running and reachable on your network.
- Python 3 installed on the client computer that will monitor the stream.
- ffmpeg installed on the client computer so recorded clips can be converted
  to browser-friendly MP4 files.

## Architecture

```text
EyeOfTheTiger
    -> GET http://eyeofthetiger.local/stream.mjpg
    -> client-side Python app
        -> OpenCV compares frames X frames apart
        -> changed area exceeds threshold
        -> save initial.jpg, second.jpg, diff.jpg
        -> record the following Y seconds of video
        -> save event metadata and MP4 in output/events/<timestamp>/

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
EyeOfTheTiger MJPEG stream at:

http://eyeofthetiger.local/stream.mjpg

Do not modify the EyeOfTheTiger server. The app must run on this client
computer and process the remote camera stream locally.

Build the project in two stages. Follow each stage exactly. Do not start stage
2 until I confirm stage 1 is working.

---

STAGE 1 - Create and test the motion detector

1. Create an app folder. Put all application code, templates, and
   requirements.txt inside app/. Create a Python virtual environment called
   .venv alongside app/. Use OpenCV for video processing.

2. Create an output/events folder. Each detected event must be stored in its
   own timestamped folder:

   output/events/YYYY-MM-DD_HH-MM-SS/

3. Create app/detector.py. It must:
   - Connect to http://eyeofthetiger.local/stream.mjpg using OpenCV.
   - Read frames continuously and reconnect after a short delay if the stream
     is interrupted.
   - Compare grayscale, blurred, downscaled frames X frames apart. Make X a
     command-line option called --frame-gap with a sensible default.
   - Use cv2.absdiff to create a visual difference image.
   - Calculate the proportion of pixels which differ by more than a
     configurable pixel threshold.
   - Trigger an event when that changed proportion exceeds a configurable
     changed-area threshold.
   - Add a configurable cooldown so one movement does not create many events.
   - When motion is detected, save:
       initial.jpg - the older frame used in the comparison
       second.jpg  - the newer frame used in the comparison
       diff.jpg    - a clear visual representation of the changed pixels
       event.json  - timestamp, thresholds, calculated score, and file names
   - Record the following Y seconds of frames from the already-open stream.
     Make Y a command-line option called --record-seconds.
   - Write the captured clip with OpenCV, then use ffmpeg to produce a
     browser-friendly H.264 MP4 named event.mp4.
   - Keep monitoring after each event until I stop it with Ctrl-C.
   - Print clear status messages when connecting, detecting motion, saving an
     event, reconnecting, and shutting down.

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
   - a note explaining the --frame-gap, --record-seconds, pixel threshold,
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
| `--frame-gap N` | 5 | Compare frames N apart. Increase to catch slower movement. |
| `--record-seconds N` | 10 | Seconds of clip to record after motion is detected. |
| `--pixel-threshold N` | 25 | Per-pixel absolute difference that counts as "changed". Increase to ignore compression noise. |
| `--changed-area-threshold F` | 0.02 | Proportion of pixels (0–1) that must change to trigger an event. Increase to reduce false positives from leaves or lighting shifts. |
| `--cooldown N` | 15 | Seconds to suppress further events after one fires. Prevents a single continuous movement from filling the event log. |

## Tuning

Motion detection needs a little tuning for the scene. A higher frame gap makes
slower movement easier to notice. A higher changed-area threshold reduces
false positives from small changes such as leaves moving or camera noise. A
cooldown keeps one continuous movement from producing a large number of clips.
