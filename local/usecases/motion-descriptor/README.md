# Motion Descriptor

A motion detection project that watches the EyeOfTheTiger MJPEG stream and
uses a locally hosted Ollama vision model to describe what changed. When
something moves in view, the app saves the two compared images and asks the
model to describe what is happening in the second image.

This example currently provides the Claude Code instructions. When the app is
generated, its implementation files should be created under `app/`.

## How it works

1. A Python application opens the EyeOfTheTiger MJPEG stream at
   `http://eyeofthetiger.local/stream.mjpg`.
2. OpenCV samples the stream and compares frames a configurable number of
   frames apart.
3. When the changed area exceeds a configurable threshold, the app saves the
   two compared frames.
4. The second image is sent to a locally hosted Ollama vision model with a
   prompt asking it to describe what is happening.
5. A small local web interface lists detected events and lets you inspect the
   initial frame, second frame, and generated description.

## What you need

- EyeOfTheTiger running and reachable on your network.
- Python 3 installed on the client computer that will monitor the stream.
- [Ollama](https://ollama.com/) installed and running on the client computer.
- A locally installed Ollama vision model, such as `gemma4`.

## Architecture

```text
EyeOfTheTiger
    -> GET http://eyeofthetiger.local/stream.mjpg
    -> client-side Python app
        -> OpenCV compares frames X frames apart
        -> changed area exceeds threshold
        -> save initial.jpg and second.jpg
        -> Ollama vision model describes second.jpg
        -> save event metadata in output/events/<timestamp>/

browser
    -> local event-review web app
        -> event list
        -> initial frame, second frame, and generated description
```

## Building it with an AI agent

Paste the following prompt into your agent, for example Claude Code, to have it
create the project for you:

```text
Build a client-side motion descriptor in this directory. Use the EyeOfTheTiger
MJPEG stream at:

http://eyeofthetiger.local/stream.mjpg

Do not modify the EyeOfTheTiger server. The app must run on this client
computer and process the remote camera stream locally.

Use a locally hosted Ollama vision model to describe motion events. Default to
the model gemma4, but make the model configurable with a command-line option.

Build the project in two stages. Follow each stage exactly. Do not start stage
2 until I confirm stage 1 is working.

---

STAGE 1 - Create and test the motion descriptor

1. Check whether Ollama is installed and running. Give me the exact commands to
   install Ollama from https://ollama.com/ if needed, and pull the default
   vision model:

   ollama pull gemma4

2. Create an app folder. Put all application code, templates, and
   requirements.txt inside app/. Create a Python virtual environment called
   .venv alongside app/. Use OpenCV for video processing and the Ollama HTTP
   API for image description.

3. Create an output/events folder. Each detected event must be stored in its
   own timestamped folder:

   output/events/YYYY-MM-DD_HH-MM-SS/

4. Create app/descriptor.py. It must:
   - Connect to http://eyeofthetiger.local/stream.mjpg using OpenCV.
   - Read frames continuously and reconnect after a short delay if the stream
     is interrupted.
   - Compare grayscale, blurred, downscaled frames X frames apart. Make X a
     command-line option called --frame-gap with a sensible default.
   - Use cv2.absdiff to measure frame changes.
   - Calculate the proportion of pixels which differ by more than a
     configurable pixel threshold.
   - Trigger an event when that changed proportion exceeds a configurable
     changed-area threshold.
   - Add a configurable cooldown so one movement does not create many events.
     Start the cooldown timer after the AI description returns, not when motion
     is first detected. If model inference takes longer than the cooldown period,
     starting the timer before the call would leave it already expired by the
     time the next frame is checked, causing immediate re-triggering.
   - When motion is detected, save:
       initial.jpg - the older frame used in the comparison
       second.jpg  - the newer frame used in the comparison
       event.json  - timestamp, thresholds, calculated score, model name,
                     generated description, and file names
   - Send second.jpg to the local Ollama API at http://localhost:11434 using a
     vision-capable model. Ask:
       "Describe what is happening in this image. Focus on people, animals,
       objects, and visible actions. Be concise and factual."
   - Default to the Ollama model gemma4. Add a --model option so I can choose a
     different locally installed vision model.
   - Handle Ollama errors cleanly. Save an error message in event.json and keep
     monitoring if the model cannot describe an image.
   - Keep monitoring after each event until I stop it with Ctrl-C.
   - Print clear status messages when connecting, detecting motion, requesting
     a description, saving an event, reconnecting, and shutting down.

5. Give me the exact commands to install dependencies and run
   app/descriptor.py.

6. Run app/descriptor.py and ask me to move in front of the camera. Wait for me to
   confirm that an event folder has been created. Then inspect the folder and
   open initial.jpg and second.jpg so I can confirm the detection looks
   reasonable. Print the generated description.

7. Ask me: "Do the captured frames and Ollama description look correct? Should
   I proceed to build the event browser?"

Wait for my answer before continuing.

---

STAGE 2 - Build the event browser (only if I said yes above)

1. Create app/app.py and any required HTML, CSS, and JavaScript files under
   app/ for a simple local web interface.

2. The interface must:
   - List detected events newest first with their timestamp and motion score.
   - Let me select an event.
   - Show the selected event's initial.jpg and second.jpg side by side with
     clear labels.
   - Show the Ollama-generated description prominently beside or below the
     images.
   - Handle the empty state when no events have been recorded.
   - Read event folders from output/events rather than requiring a database.
   - Serve saved images through the application.
   - Use a clean, compact layout that works on desktop and mobile screens.

3. Add a short README section containing:
   - Ollama setup commands
   - Python setup commands
   - the command to run app/descriptor.py
   - the command to run the event browser
   - the local URL for the browser
   - a note explaining the --model, --frame-gap, pixel threshold,
     changed-area threshold, and cooldown options

4. Run the browser locally and open it for me. Verify that the test event is
   listed and that the two images and description can be viewed.
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
# From the motion-descriptor/ directory
python3 -m venv .venv
.venv/bin/pip install -r app/requirements.txt
```

### Run the motion descriptor

```bash
.venv/bin/python app/descriptor.py
```

### Run the event browser

```bash
.venv/bin/python app/app.py
```

Open **http://localhost:5001** in your browser.

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--model` | `gemma4` | Ollama vision model to use for descriptions |
| `--frame-gap` | `10` | Number of frames between the two compared frames. Increase to catch slower movement. |
| `--pixel-threshold` | `25` | Per-pixel brightness difference (0–255) required to count a pixel as changed. |
| `--area-threshold` | `0.02` | Fraction of pixels that must have changed to trigger an event (0.02 = 2%). Increase to reduce false positives from leaves, lighting shifts, etc. |
| `--cooldown` | `30` | Minimum seconds between events so one continuous movement does not flood the output folder. |

Example with custom options:

```bash
.venv/bin/python app/descriptor.py --model gemma4 --frame-gap 15 --area-threshold 0.03 --cooldown 20
```

## Tuning

Motion detection needs a little tuning for the scene. A higher frame gap makes
slower movement easier to notice. A higher changed-area threshold reduces
false positives from small changes such as leaves moving or camera noise. A
cooldown keeps one continuous movement from producing many descriptions.
