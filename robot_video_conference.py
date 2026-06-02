#!/usr/bin/env python3
"""
Integrated AI-powered video conferencing application for the TurboPi robot.

This script combines three core pieces of functionality:

1. Face detection and robot control: it captures frames from the TurboPi
   onboard camera, uses MediaPipe to detect faces, and uses PID controllers to
   adjust both the pan-tilt servos and the mecanum chassis so the largest face
   remains centered in the frame.

2. Video streaming: it exposes the live video feed over WebRTC using aiortc.
   When a remote browser connects, the script negotiates an SDP offer/answer
   exchange and streams frames produced by the face-tracking loop.

3. Async event loop: frame acquisition, face detection, robot control, and
   WebRTC streaming run in the same asyncio event loop.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from fractions import Fraction
from typing import Optional, Tuple

import cv2
import numpy as np
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
from av import VideoFrame

try:
    import mediapipe as mp
except ImportError:
    mp = None  # type: ignore[assignment]


SDK_IMPORT_ERROR: Optional[Exception] = None

try:
    import HiwonderSDK.PID as PID
    import HiwonderSDK.mecanum as mecanum
    import HiwonderSDK.ros_robot_controller_sdk as rrc
except Exception as exc:
    mecanum = None  # type: ignore[assignment]
    PID = None  # type: ignore[assignment]
    rrc = None  # type: ignore[assignment]
    SDK_IMPORT_ERROR = exc


logger = logging.getLogger("robot_video_conference")
ROOT = os.path.dirname(os.path.abspath(__file__))
pcs = set()
relay = MediaRelay()

robot: Optional["RobotController"] = None


class RobotController:
    """Encapsulates camera capture, face detection, and robot control."""

    def __init__(self, camera_index: int = 0, frame_size: Tuple[int, int] = (640, 480)):
        self.frame_size = frame_size
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            logger.warning("Unable to open camera %d; face tracking will be disabled", camera_index)

        if mp is None:
            self.face_detection = None
            logger.warning("MediaPipe is not installed; face tracking will be disabled")
        else:
            self.face_detection = mp.solutions.face_detection.FaceDetection(
                min_detection_confidence=0.5
            )

        self.board = None
        self.car = None
        if SDK_IMPORT_ERROR is not None:
            logger.warning("Hiwonder SDK is unavailable; hardware control disabled: %s", SDK_IMPORT_ERROR)

        if mecanum and PID and rrc:
            try:
                self.board = rrc.Board()
                self.car = mecanum.MecanumChassis(self.board)
                self.car_x_pid = PID.PID(P=0.15, I=0.001, D=0.0001)
                self.car_y_pid = PID.PID(P=0.002, I=0.001, D=0.0001)
                self.servo_x_pid = PID.PID(P=0.1, I=0.0, D=0.0)
                self.servo_y_pid = PID.PID(P=0.1, I=0.0, D=0.0)
                self.servo_pitch = 1500
                self.servo_yaw = 1500
            except Exception as exc:
                logger.warning("TurboPi hardware initialization failed; hardware control disabled: %s", exc)
                self.board = None
                self.car = None

        self.servo_min = 500
        self.servo_max = 2500

    def _update_servos(self, dx: float, dy: float) -> None:
        """Update servo positions based on the face offset."""
        if self.board is None:
            return

        pitch_adjust = self.servo_y_pid.PID_compute(-dy)
        yaw_adjust = self.servo_x_pid.PID_compute(dx)
        self.servo_pitch += pitch_adjust
        self.servo_yaw += yaw_adjust
        self.servo_pitch = max(self.servo_min, min(self.servo_max, int(self.servo_pitch)))
        self.servo_yaw = max(self.servo_min, min(self.servo_max, int(self.servo_yaw)))

        try:
            self.board.pwm_servo_set_position(0.5, [[1, self.servo_pitch], [2, self.servo_yaw]])
        except Exception as exc:
            logger.error("Failed to set servo positions: %s", exc)

    def _update_chassis(self, dx: float, dy: float) -> None:
        """Move the chassis to center the face if the offset is large."""
        if self.car is None:
            return

        vx = self.car_x_pid.PID_compute(dx)
        vy = self.car_y_pid.PID_compute(dy)
        max_v = 50
        vx = max(-max_v, min(max_v, vx))
        vy = max(-max_v, min(max_v, vy))

        try:
            self.car.translation(vx, vy)
        except Exception as exc:
            logger.error("Failed to command chassis: %s", exc)

    def get_frame(self) -> np.ndarray:
        """Capture a frame, perform face detection, and control the robot."""
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return np.zeros((self.frame_size[1], self.frame_size[0], 3), dtype=np.uint8)

        if self.face_detection is None:
            return frame

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb)

        if results.detections:
            largest = None
            max_area = 0
            for det in results.detections:
                bbox = det.location_data.relative_bounding_box
                x, y, width, height = (
                    bbox.xmin * w,
                    bbox.ymin * h,
                    bbox.width * w,
                    bbox.height * h,
                )
                area = width * height
                if area > max_area:
                    max_area = area
                    largest = (x, y, width, height)

            if largest:
                x, y, width, height = largest
                cv2.rectangle(
                    frame,
                    (int(x), int(y)),
                    (int(x + width), int(y + height)),
                    (0, 255, 0),
                    2,
                )

                face_cx = x + width / 2
                face_cy = y + height / 2
                center_x = w / 2
                center_y = h / 2
                dx = (face_cx - center_x) / center_x
                dy = (face_cy - center_y) / center_y

                self._update_servos(dx, dy)
                if abs(dx) > 0.2 or abs(dy) > 0.2:
                    self._update_chassis(dx, dy)

        return frame


class RobotVideoStreamTrack(MediaStreamTrack):
    """Video stream track sourcing frames from a RobotController."""

    kind = "video"

    def __init__(self, robot_controller: RobotController):
        super().__init__()
        self.robot = robot_controller
        self._pts = 0
        self._time_base = Fraction(1, 30)

    async def recv(self) -> VideoFrame:
        await asyncio.sleep(float(self._time_base))
        frame = self.robot.get_frame()
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        self._pts += 1
        video_frame.pts = self._pts
        video_frame.time_base = self._time_base
        return video_frame


async def index(request: web.Request) -> web.Response:
    content = open(os.path.join(ROOT, "index.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)


async def client_js(request: web.Request) -> web.Response:
    content = open(os.path.join(ROOT, "client.js"), "r", encoding="utf-8").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request: web.Request) -> web.Response:
    if robot is None:
        return web.json_response(
            {"error": "Robot controller is not initialized"},
            status=503,
        )

    params = await request.json()
    offer_description = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info("Received offer from %s", request.remote)

    pc.addTrack(relay.subscribe(RobotVideoStreamTrack(robot)))

    @pc.on("connectionstatechange")
    async def on_connectionstatechange() -> None:
        logger.info("Connection state changed to %s", pc.connectionState)
        if pc.connectionState in ("failed", "closed", "disconnected"):
            await pc.close()
            pcs.discard(pc)

    await pc.setRemoteDescription(offer_description)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}),
    )


async def on_shutdown(app: web.Application) -> None:
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


def main() -> None:
    global robot

    logging.basicConfig(level=logging.INFO)
    robot = RobotController()

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", client_js)
    app.router.add_post("/offer", offer)

    port = int(os.environ.get("SIGNAL_PORT", 8080))
    logger.info("TurboPi video conference server starting on port %d", port)
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
