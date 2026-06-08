# Person Spotted Notification

A motion detection project that watches the EyeOfTheTiger MJPEG stream and
uses a locally hosted Ollama vision model to check whether a person is present.
When a person is detected, the app records 10 seconds of video and posts it to
a Slack channel with a "Person spotted" alert message.

This example provides the Claude Code instructions. When the app is generated,
its implementation files should be created under `app/`.

## How it works

1. A Python application opens the EyeOfTheTiger MJPEG stream at
   `http://eyeofthetiger.local/v1/stream.mjpg`.
2. OpenCV samples the stream and compares frames a configurable number of
   frames apart.
3. When the changed area exceeds a configurable threshold, the two frames are
   saved and the newer image is sent to a locally hosted Ollama vision model.
4. The model is asked to check whether a person is visible and must respond
   with a JSON object containing a single boolean field: `{"person": true}` or
   `{"person": false}`.
5. If `person` is `true`, the app opens the stream again, captures frames for
   a configurable duration, measures the actual frame rate, and writes a video
   at that measured FPS so playback is real-time.
6. The video is posted to a configured Slack channel using a Slack bot token.
7. A cooldown prevents the same continuous presence from flooding Slack.

## What you need

- EyeOfTheTiger running and reachable on your network.
- Python 3 installed on the client computer that will monitor the stream.
- [Ollama](https://ollama.com/) installed and running on the client computer.
- A locally installed Ollama vision model, such as `gemma4`.
- A Slack workspace with a bot token and a target channel (see setup below).

## Slack setup

You need to create a Slack app and give it permission to upload files and post
messages before running this project.

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click
   **Create New App** → **From scratch**. Give it a name (e.g. "Person
   Spotter") and choose your workspace.
2. In the left sidebar go to **OAuth & Permissions**. Under **Bot Token
   Scopes** add:
   - `chat:write` — post messages
   - `files:write` — upload images
3. Scroll to the top of **OAuth & Permissions** and click **Install to
   Workspace**, then **Allow**.
4. Copy the **Bot User OAuth Token** (it starts with `xoxb-`). This is your
   `SLACK_BOT_TOKEN`.
5. Invite the bot to your target channel in Slack by typing
   `/invite @YourBotName` in that channel.
6. Find your channel ID: right-click the channel name → **View channel
   details** → scroll to the bottom. Copy the ID (starts with `C`). This is
   your `SLACK_CHANNEL_ID`.
7. Set both values as environment variables before running the app:

```bash
export SLACK_BOT_TOKEN=xoxb-your-token-here
export SLACK_CHANNEL_ID=C0123456789
```

## Architecture

```text
EyeOfTheTiger
    -> GET http://eyeofthetiger.local/v1/stream.mjpg
    -> client-side Python app
        -> OpenCV compares frames X frames apart
        -> changed area exceeds threshold
        -> save initial.jpg and second.jpg
        -> Ollama vision model checks for a person in second.jpg
        -> model returns {"person": true/false}
        -> if person: true
            -> capture N seconds of stream frames into a buffer
            -> measure actual FPS from elapsed time
            -> write event.mp4 at measured FPS (real-time playback)
            -> post event.mp4 to Slack with "Person spotted" message
        -> save event metadata in output/events/<timestamp>/
```

## Building it with an AI agent

Paste the following prompt into your agent, for example Claude Code, to have it
create the project for you:

```text
Build a client-side person-detection notifier in this directory. Use the
EyeOfTheTiger MJPEG stream at:

http://eyeofthetiger.local/v1/stream.mjpg

Do not modify the EyeOfTheTiger server. The app must run on this client
computer and process the remote camera stream locally.

Use a locally hosted Ollama vision model to check whether a person is present
after motion is detected. When a person is confirmed, post the image to Slack.

Build the project in two stages. Follow each stage exactly. Do not start stage
2 until I confirm stage 1 is working.

---

STAGE 1 - Create and test the motion detector and person classifier

1. Check whether Ollama is installed and running. Give me the exact commands
   to install Ollama from https://ollama.com/ if needed, and pull the default
   vision model:

   ollama pull gemma4

2. Create an app folder. Put all application code and requirements.txt inside
   app/. Create a Python virtual environment called .venv alongside app/. Use
   OpenCV for video processing and the Ollama HTTP API for person detection.

3. Create an output/events folder. Each detected event must be stored in its
   own timestamped folder:

   output/events/YYYY-MM-DD_HH-MM-SS/

4. Create app/detector.py. It must:
   - Connect to http://eyeofthetiger.local/stream.mjpg using OpenCV.
   - Read frames continuously and reconnect after a short delay if the stream
     is interrupted.
   - Compare grayscale, blurred, downscaled frames X frames apart. Make X a
     command-line option called --frame-gap with a sensible default.
   - Use cv2.absdiff to measure frame changes.
   - Calculate the proportion of pixels which differ by more than a
     configurable pixel threshold.
   - Trigger a check when that changed proportion exceeds a configurable
     changed-area threshold.
   - Add a configurable cooldown so one movement does not create many events.
     Start the cooldown timer after the AI classification returns, not when
     motion is first detected. If model inference takes longer than the
     cooldown period, starting the timer before the call would leave it already
     expired by the time the next frame is checked, causing immediate
     re-triggering.
   - When motion is detected, save:
       initial.jpg  - the older frame used in the comparison
       second.jpg   - the newer frame used in the comparison
   - Send second.jpg to the local Ollama API at http://localhost:11434 using a
     vision-capable model. Use this exact prompt:
       "Look at this image and determine whether there is a person visible.
       Respond with valid JSON only, no other text. The JSON must have a single
       boolean field: {\"person\": true} if a person is visible, or
       {\"person\": false} if not."
   - Parse the model's response as JSON and extract the boolean "person" field.
     If the response cannot be parsed, treat it as {"person": false} and log a
     warning. Do not crash on a bad response.
   - Save an event.json file in the event folder containing: timestamp,
     model name, motion score, thresholds, frame gap, cooldown, image file
     names, the raw model response string, and the parsed person boolean.
   - Default to the Ollama model gemma4. Add a --model option so I can choose
     a different locally installed vision model.
   - Add a --video-duration option (default 10.0) controlling how many seconds
     of video to capture when a person is confirmed.
   - Handle Ollama errors cleanly. Save an error message in event.json and keep
     monitoring if the model cannot classify an image.
   - Keep monitoring after each event until I stop it with Ctrl-C.
   - Print clear status messages when connecting, detecting motion, calling
     Ollama, parsing the result, saving an event, reconnecting, and shutting
     down.

5. Give me the exact commands to install dependencies and run app/detector.py.

6. Run app/detector.py and ask me to move in front of the camera. Wait for me
   to confirm that an event folder has been created. Inspect the event.json and
   print its contents so I can confirm the detection is working and the person
   field is being set correctly.

7. Ask me: "Does the person classification look correct? Should I proceed to
   add Slack notifications?"

Wait for my answer before continuing.

---

STAGE 2 - Add Slack notifications (only if I said yes above)

1. Before writing any code, tell the user that they will need a Slack bot token
   and channel ID, and point them to the "Slack setup" section of the README in
   this directory for step-by-step instructions on creating the app and finding
   these values.

2. Read the Slack bot token and channel ID from environment variables:
     SLACK_BOT_TOKEN   - the bot user OAuth token (starts with xoxb-)
     SLACK_CHANNEL_ID  - the channel ID to post to (starts with C)

   If either variable is missing, print a clear error message explaining how to
   set them and exit. Do not hardcode tokens in the source.

3. Create app/slack_poster.py. Put all Slack logic there and import it from
   detector.py. It must contain a send_slack_alert(video_path, timestamp)
   function that accepts a single Path to a video file and:
   - Uploads the file to Slack using files.getUploadURLExternal and
     files.completeUploadExternal (the current Slack file upload API).
     Do not use the deprecated files.upload method.
   - IMPORTANT: files.getUploadURLExternal requires form-encoded parameters
     (use data= in requests, not json=). Sending JSON will return an
     invalid_arguments error from Slack.
   - Posts to SLACK_CHANNEL_ID with initial_comment:
     "Person spotted at <timestamp>"
   - Handles Slack API errors cleanly and prints a warning without crashing if
     the upload fails.

4. In the main detection loop, when the person field is true:
   - Open the stream and collect frames into a list for --video-duration
     seconds.
   - Measure the actual frame rate as frame_count / elapsed_seconds. Do NOT
     hardcode the FPS — MJPEG streams often deliver fewer frames than expected
     due to network or Pi load, so a hardcoded value will produce slow-motion
     or fast-motion video.
   - Write the collected frames to event.mp4 using cv2.VideoWriter at the
     measured FPS so playback is real-time.
   - Call send_slack_alert with the video path.

5. Update event.json to include a "slack_posted" boolean indicating whether the
   Slack notification was sent successfully.

6. Give me the exact commands to set the environment variables and restart
   detector.py.

7. Run detector.py, walk in front of the camera, and wait for me to confirm
   that a Slack message with the image appears in the channel.

8. Ask me: "Did the Slack notification arrive with the image? Is everything
   working as expected?"
```

## Setup and usage

### Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the default vision model
ollama pull gemma4
```

### Monitoring Ollama

Ollama runs as a systemd service by default. To watch its output live:

```bash
journalctl -u ollama -f
```

Alternatively, stop the service and run Ollama directly in a terminal so logs
print inline:

```bash
sudo systemctl stop ollama
ollama serve
# restore the service later:
sudo systemctl start ollama
```

### Python environment

```bash
# From the person-spotted-notification/ directory
python3 -m venv .venv
.venv/bin/pip install -r app/requirements.txt
```

### Slack credentials

```bash
export SLACK_BOT_TOKEN=xoxb-your-token-here
export SLACK_CHANNEL_ID=C0123456789
```

### Run the detector

```bash
.venv/bin/python app/detector.py
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--model` | `gemma4` | Ollama vision model to use for person detection |
| `--frame-gap` | `5` | Number of frames between the two compared frames. Increase to catch slower movement. |
| `--pixel-threshold` | `25` | Per-pixel brightness difference (0–255) required to count a pixel as changed. |
| `--area-threshold` | `0.02` | Fraction of pixels that must have changed to trigger a check (0.02 = 2%). |
| `--cooldown` | `10` | Minimum seconds between events so continuous presence does not flood Slack. |
| `--video-duration` | `10.0` | Seconds of video to capture and post when a person is confirmed. |

Example with custom options:

```bash
.venv/bin/python app/detector.py --model gemma4 --frame-gap 15 --area-threshold 0.03 --cooldown 60
```

## Tuning

Motion detection needs a little tuning for the scene. A higher frame gap makes
slower movement easier to notice. A higher changed-area threshold reduces false
positives from small changes such as leaves moving or lighting shifts. Raise the
cooldown if you are getting repeated Slack notifications from the same person
standing still.

If the model is misclassifying, try a more capable vision model. Some smaller
models may not reliably return valid JSON — a larger model or one fine-tuned for
instruction following will behave more consistently.

Video playback speed is automatically correct because the app measures actual
frames received over elapsed time and writes the MP4 at that rate. If the
stream is slow due to network conditions or Pi load, the video will simply be
lower resolution in time — but it will not play back in slow motion or fast
forward. The measured FPS is logged at capture time if you want to check it.
