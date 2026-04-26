# Flask + webRTC signaling server for AIZeeBot

from flask import Flask, render_template , request
from aiortc import RTCPeerConnection, RTCSessionDescription
from webrtc_server import CameraStreamTrack

app = Flask(__name__)
pcs = set()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/offer", methods=["POST"])
async def offer():
    params = request.get_json()

    pc = RTCPeerConnection()
    pcs.add(pc)

    pc.addTrack(CameraStreamTrack())

    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"]
    )

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)