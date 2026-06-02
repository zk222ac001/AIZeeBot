#!/usr/bin/env python3
"""
Simple WebRTC signaling server for the TurboPi video conferencing demo.

This script exposes a minimal HTTP server that serves a web client and handles
SDP offer/answer exchange for WebRTC. When the client sends an offer via
POST /offer, the server creates a new RTCPeerConnection, attaches a video track,
and returns the SDP answer.
"""

import asyncio
import json
import logging
import os
from fractions import Fraction

import cv2
import numpy as np
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
from av import VideoFrame

ROOT = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger("robot_server")
pcs = set()
relay = MediaRelay()


class RobotVideoStreamTrack(MediaStreamTrack):
    """A video track that reads frames from the Raspberry Pi camera."""

    kind = "video"

    def __init__(self, camera_index: int = 0):
        super().__init__()
        self.cap = cv2.VideoCapture(camera_index)
        self._pts = 0
        self._time_base = Fraction(1, 30)
        if not self.cap.isOpened():
            logger.warning("Camera could not be opened, using blank frames")

    async def recv(self) -> VideoFrame:
        await asyncio.sleep(float(self._time_base))
        ret, frame = self.cap.read()
        if not ret:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

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
    params = await request.json()
    offer_description = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info("Created peer connection for %s", request.remote)

    video_track = RobotVideoStreamTrack()
    pc.addTrack(relay.subscribe(video_track))

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
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", client_js)
    app.router.add_post("/offer", offer)

    port = int(os.environ.get("SIGNAL_PORT", 8080))
    logger.info("Starting server on port %d", port)
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
