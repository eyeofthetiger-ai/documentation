# Network and USB Cameras

An EOT-1 runs its own camera plus IP cameras on your network and USB webcams
plugged into it. Each one gets snapshots, clips, live view, continuous
recording, the library and events, and apps can use any of them.

## Camera ids

A camera's id is your EOT-1's id plus its name on it: `eot-a3f9c2d1-door`. The
EOT-1's own camera is `eot-a3f9c2d1-main`. The bare id, `eot-a3f9c2d1`, means
the **default** camera, so existing scripts keep working. Use these ids
anywhere a `camera_id` goes (REST paths and MCP tools). `list_cameras` lists
every camera in your account.

## Add a camera

In the portal: open your EOT-1, **Settings** > **Cameras**, give it a name and a
stream address, then **Add camera**.

| Camera | Stream address |
|---|---|
| IP camera | `rtsp://user:password@192.168.1.20:554/stream1` (also `rtsps://`) |
| HTTP camera | `http://192.168.1.21/video.mjpg` |
| USB webcam | `/dev/videoN` (`v4l2-ctl --list-devices` on the EOT-1, or `GET /v1/cameras/usb-devices`) |

A network camera can also have a low-resolution `sub_url`, used for the live
preview and quick snapshots. Passwords stay on the EOT-1 and are never shown back.

Or with the API (organisation admin; `eot-a3f9c2d1` is the EOT-1's id):

```bash
curl -X POST https://platform.eyeofthetiger.ai/api/v1/cameras/eot-a3f9c2d1/cameras \
  -H "x-api-key: $KEY" -H "Content-Type: application/json" \
  -d '{"id":"door","name":"Door","url":"rtsp://user:pass@192.168.1.20:554/stream1"}'

# Check it works (redirects to a snapshot from it)
curl -L -X POST https://platform.eyeofthetiger.ai/api/v1/cameras/eot-a3f9c2d1/cameras/door/test \
  -H "x-api-key: $KEY" -o test.jpg
```

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/cameras/{id}/cameras` | The EOT-1's cameras |
| POST | `/api/v1/cameras/{id}/cameras` | Add one |
| PATCH | `/api/v1/cameras/{id}/cameras/{sourceId}` | Change one (409 while it is recording or live) |
| DELETE | `/api/v1/cameras/{id}/cameras/{sourceId}` | Remove one; its recordings stay |
| PUT | `/api/v1/cameras/{id}/cameras/default?source_id=door` | Choose the default |
| POST | `/api/v1/cameras/{id}/cameras/{sourceId}/test` | Snapshot to check it works |

`continuous-recording/start` and `stop` also take `source_id=door`. A camera id
is lowercase letters, digits and hyphens, up to 32 characters. The EOT-1's own
camera, `main`, can only be renamed.

## Options

| Field | For | Meaning |
|---|---|---|
| `sub_url` | network | Low-resolution stream |
| `record_stream` | network with a `sub_url` | `main` (default), `sub` or `both`: what recordings and clips copy |
| `input_format` | USB | `mjpeg` (default if offered), `yuyv422`, ... |
| `video_size`, `fps` | USB | e.g. `1280x720`, 1 to 120 |
| `encoder` | USB | `libx264` or `h264_v4l2m2m` |

Camera details include `default`, `record_stream` and `available_streams`.

## Cabling IP cameras to the EOT-1

Run `install_scripts/eot-camera-network.sh` on the EOT-1. Its Ethernet port
becomes a private camera network (192.168.50.1/24, cameras get 192.168.50.10 to
.50), nothing is routed to or from the internet, and the EOT-1 is the cameras'
time server: set each camera's NTP server to `192.168.50.1` and its timezone,
or the time on its picture will be wrong. Then add each camera by its RTSP address.

## Good to know

- Several cameras can record at once and share one storage limit.
- One camera at a time can be live streamed through the portal.
- Only the EOT-1's own camera follows the quality setting.
- Cameras recorded as-is (H.264 or H.265) cost little; USB webcams are encoded on the EOT-1.
