/*
 * Minimal WebRTC client to display the TurboPi video stream.
 *
 * When the page loads, it creates an RTCPeerConnection and gathers ICE
 * candidates.  It then creates an SDP offer and sends it to the server via
 * ``POST /offer``.  The server responds with an SDP answer containing the
 * robot’s video track.  Once the connection is established, incoming
 * video frames are assigned to the <video> element on the page.
 */

async function startCall() {
  const pc = new RTCPeerConnection();

  // Display the remote video when tracks arrive
  pc.ontrack = (event) => {
    const video = document.getElementById('remoteVideo');
    if (video.srcObject !== event.streams[0]) {
      video.srcObject = event.streams[0];
    }
  };

  // Create an offer and set the local description
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  // Send the offer to the server
  const response = await fetch('/offer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sdp: pc.localDescription.sdp,
      type: pc.localDescription.type,
    }),
  });
  const answer = await response.json();
  await pc.setRemoteDescription(answer);
}

window.addEventListener('load', () => {
  startCall().catch((err) => console.error(err));
});