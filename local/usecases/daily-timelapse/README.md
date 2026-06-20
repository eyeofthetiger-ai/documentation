# Daily Time-lapse Creator

A pure-API project that captures frames from the EyeOfTheTiger throughout the day and stitches them into an MP4 at midnight. The finished video can either be uploaded to Google Drive or saved to a local directory — your choice. No AI model required — the camera is used as a plain data source.

We have included the code created by pasting the instructions below into Claude
Code in the [`app/`](app/) folder.

## How it works

1. A cron job runs every 2 minutes during daylight hours and saves a JPEG from the HTTP snapshot endpoint.
2. At midnight a second cron job runs ffmpeg to stitch the day's frames into a time-lapse MP4.
3. The video is either uploaded to a Google Drive folder **or** moved to a local output directory, then the day's frames are archived or deleted.

## What you need

- EyeOfTheTiger running and reachable on your network.
- ffmpeg installed on the machine running the scripts.
- **For Google Drive upload only:** A Google Cloud project with the Drive API enabled and a service account JSON key, plus Python 3 with `google-auth` and `googleapiclient`.

## Architecture

```
cron (every 2 min)
    → app/capture.sh
        → GET http://eyeofthetiger.local/v1/snapshot
        → save to output/frames/YYYY-MM-DD/HH-MM.jpg

cron (00:05 daily)
    → app/stitch.sh
        → ffmpeg: frames → YYYY-MM-DD.mp4
        → [Google Drive] app/upload.py: mp4 → Google Drive folder
          OR
          [Local]        move mp4 → output/timelapse
        → clean up frames
```

## Building it with an AI agent

Paste the following prompt into your agent (e.g. Claude Code) to have it create the project for you:

```
Build a daily time-lapse system in two stages. Follow each stage exactly — do not
start stage 2 until I confirm stage 1 is working.

---

STAGE 1 — Create and test the capture script

1. Create a folder called `app` in the same directory as this README. Create an
   `output` folder alongside it, with subfolders called `frames` and `timelapse`.

2. Create app/capture.sh — a shell script that:
   - Fetches a JPEG from http://eyeofthetiger.local/v1/snapshot using curl.
   - Saves it to output/frames/$(date +%Y-%m-%d)/$(date +%H-%M).jpg.

3. Run app/capture.sh once to grab a test frame using `bash app/capture.sh` (no chmod
   needed — always invoke it with bash directly), then open the saved JPEG so I
   can see it (use xdg-open on Linux, open on macOS).

4. Ask me: "Does the image look correct? Should I proceed to set up scheduling
   and stitching?"

   Wait for my answer before continuing.

---

STAGE 2 — Scheduling and stitching (only if I said yes above)

Before writing any further code, ask me one question:

  "Where should the finished time-lapse MP4 be stored — uploaded to Google Drive,
   or saved to a local output folder (output/timelapse)?"

Wait for my answer, then build the stiching script:

app/stitch.sh — a shell script that:
   - Takes an optional date argument (default: yesterday, formatted YYYY-MM-DD).
   - Runs ffmpeg to combine all JPEGs in output/frames/<date>/ into a time-lapse MP4
     at 24fps named <date>.mp4 in output/timelapse/.
   - Calls the appropriate storage step depending on the chosen option (see below).


After that, give me instructions on how to write a crontab snippet scheduling
   app/capture.sh every 2 minutes from 06:00 to 21:00 and app/stitch.sh at 00:05
   daily. Then tell me how to open crontab and how to save the snippet.

Next tell me the following:

  "Important: do not try to test app/stitch.sh yet. At 2-minute capture intervals
   and 24 fps output, the video will be invisible to most players until at least
   24 frames have accumulated (roughly 4 hours of capture). A full day produces
   ~90 frames — about 4 seconds of video. Set up the crontab now and run
   app/stitch.sh manually tomorrow morning to verify the first full timelapse."

---

IF the user chose Google Drive, additionally build:

3. app/upload.py — a Python script that:
   - Accepts a file path as a command-line argument.
   - Uploads the file to a Google Drive folder whose ID is in the environment variable
     GOOGLE_DRIVE_FOLDER_ID, using a service account key at the path in
     GOOGLE_SERVICE_ACCOUNT_KEY.
   - Prints the Drive file URL on success.
- app/stitch.sh should call app/upload.py after ffmpeg completes.
- A .env.example with GOOGLE_DRIVE_FOLDER_ID and GOOGLE_SERVICE_ACCOUNT_KEY.
- An app/requirements.txt for upload.py.

IF the user chose local save, instead:
- app/stitch.sh should move the finished MP4 to output/timelapse.
- No upload.py, no .env.example, no requirements.txt needed.
```



## Scheduling

### Stop (pause or remove the cron jobs)

To **pause** without losing the configuration, open the crontab and comment out the lines:

```bash
crontab -e
# prefix the lines with # to disable them
```

To **remove** the jobs entirely, delete those lines from the crontab and save (ctrl-X, Enter, ctrl-O).
