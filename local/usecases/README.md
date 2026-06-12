# Use Cases

These use cases show ways to use EyeOfTheTiger as a camera source for scripts,
local applications, and AI agents. They use the **local** device API
(`http://eyeofthetiger.local/...`); for quick endpoint smoke tests see
[`../minimal_examples/`](../minimal_examples/).

For scaffolded use cases, we have included the code created by pasting the
instructions into Claude Code under the example's `app/` folder.

## Use cases

- [Daily Time-lapse Creator](daily-timelapse/README.md): capture images
  throughout the day and stitch them into a video.
- [Motion Detection Event Recorder](motion-detect/README.md): detect motion
  locally, record short clips, and review captured events in a browser.
- [Motion Descriptor](motion-descriptor/README.md): detect motion locally and
  use an Ollama vision model to describe each event.
- [Person Spotted Notification](person-spotted-notification/README.md): detect
  motion locally, use an Ollama vision model to check for a person, and post an
  alert image to Slack when one is found.
- [Kitchen Assistant](kitchen-assistant/README.md): a conversational cooking
  assistant that uses the MCP `take_snapshot` tool to look at your worktop on
  request.

## Ideas

These are starting points for projects you could build with EyeOfTheTiger.

### Plant Monitor

Capture an image of a plant once a day and ask a vision model whether the soil
or leaves look dry. Send a Slack message when watering may be needed.

### Wildlife Sighting Logger

Point the camera at a garden, bird feeder, or window. Capture images on a
schedule, ask a vision model to identify visible wildlife, and append sightings
to a Google Sheet with a timestamp, description, and confidence level.

### Package Detector

Point the camera at a front door or porch. Check the image every few minutes
and use a vision model to identify packages. Send a Slack, email, or SMS
notification when a parcel appears, and reset the alert after it is collected.

### Home Security Alert

Use an OpenClaw agent to capture images periodically and look for unexpected
people, open doors, fallen objects, or other concerns. Send a Slack alert when
the agent notices something unusual.
