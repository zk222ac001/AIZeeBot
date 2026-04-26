import cv2
# Enables asynchronous programming (required for WebRTC streaming).
import asyncio
import logging
import numpy as np
# You extend this to create a custom video stream.
from aiortc import VideoStreamTrack
# Converts NumPy frames into WebRTC-compatible frames.
from av import VideoFrame

logger = logging.getLogger(__name__)

class CameraStreamTrack(VideoStreamTrack):
    """WebRTC video stream from camera with fallback to black frame."""
    
    def __init__(self, camera_id=0, width=640, height=480, fps=30):
        """
        Args:
            camera_id: Camera device index
            width: Frame width
            height: Frame height
            fps: Frames per second
        """
        if not isinstance(camera_id, int) or camera_id < 0:
            raise ValueError("camera_id must be a non-negative integer")
        
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        
        if fps <= 0:
            raise ValueError("fps must be positive")
        
        super().__init__()
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera {camera_id}")
            raise RuntimeError(f"Cannot open camera {camera_id}")

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to read frame, using black frame")
                frame = self._black_frame()
            else:
                frame = cv2.resize(frame, (self.width, self.height))
                frame = frame.astype(np.uint8)
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            frame = self._black_frame()
        
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        
        await asyncio.sleep(1 / self.fps)
        return video_frame

    def _black_frame(self):
        """Return a black frame as fallback."""
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def stop(self):
        super().stop()
        if self.cap.isOpened():
            self.cap.release()
            logger.info("Camera released")