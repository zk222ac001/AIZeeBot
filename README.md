# AI-Powered Robotic Video Conferencing System

This project is a proof-of-concept video conferencing system for the Hiwonder
TurboPi robot. It combines a browser-based WebRTC video stream with optional
face detection and robot control for the TurboPi pan-tilt camera and mecanum
wheel chassis.

The code can run in two modes:

- `server.py` starts a simple WebRTC camera server.
- `robot_video_conference.py` starts the integrated robot controller, face
  tracking loop, and WebRTC server.

When the app is started on a machine without a camera, MediaPipe, or TurboPi
hardware attached, it falls back gracefully: the server still starts, camera
frames fall back to blank video, and robot tracking/control is disabled.

## Features

- WebRTC video streaming with `aiohttp`, `aiortc`, and `av`.
- Camera capture through OpenCV.
- Optional MediaPipe face detection.
- Optional TurboPi hardware control through the Hiwonder SDK.
- Safe fallback behavior for development machines without robot hardware.

## Project Files

```text
.
|-- README.md
|-- server.py
|-- robot_video_conference.py
|-- index.html
|-- client.js
`-- HiwonderSDK/
    |-- mecanum.py
    |-- PID.py
    `-- ros_robot_controller_sdk.py
```

## Install

On the TurboPi or Raspberry Pi, install the system packages and Python
dependencies:

```bash
sudo apt update
sudo apt install python3-opencv python3-pip
pip3 install aiohttp aiortc av numpy mediapipe pyserial
```

MediaPipe is optional for local development, but it is required for face
tracking. The robot hardware control path also requires the Hiwonder SDK and
access to the TurboPi serial controller.

## Run The Basic Video Server

```bash
python3 server.py
```

Open this URL from another device on the same network:

```text
http://<pi_ip>:8080
```

## Run The Integrated Robot App

```bash
python3 robot_video_conference.py
```

Then open:

```text
http://<robot_ip>:8080
```

The browser page creates a WebRTC connection and displays the robot camera
feed. If MediaPipe and TurboPi hardware are available, the robot attempts to
keep the detected face centered using the pan-tilt servos and chassis control.

## Configuration

Set `SIGNAL_PORT` to change the HTTP/WebRTC signaling port:

```bash
SIGNAL_PORT=8090 python3 robot_video_conference.py
```

## Notes

This is a prototype. For production use, add authentication, HTTPS, proper
multi-client signaling, audio support, and stronger safety checks around robot
movement.
