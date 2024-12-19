import asyncio
import cv2
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import BYE
from av import VideoFrame

pcs = set()  # Keep track of active peer connections

# Video track from OpenCV
class VideoStream(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)  # Change to your video source

    async def recv(self):
        # Capture frame
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Camera Error")
        
        # Convert frame to VideoFrame (required by WebRTC)
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts, video_frame.time_base = 0, 1 / 30  # Set frame rate (30 FPS)
        return video_frame

# Handle WebRTC offer
async def offer(request):
    params = await request.json()  # Receive the SDP offer from the client
    pc = RTCPeerConnection()
    pcs.add(pc)

    # Add the video stream to the connection
    pc.addTrack(VideoStream())

    # Handle the offer and create an answer
    await pc.setRemoteDescription(RTCSessionDescription(sdp=params["sdp"], type=params["type"]))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(content_type="application/json", text=pc.localDescription.sdp)

# Clean up connections
async def on_shutdown(app):
    for pc in pcs:
        await pc.close()
    pcs.clear()

# Set up the server
app = web.Application()
app.on_shutdown.append(on_shutdown)
app.add_routes([web.post("/offer", offer)])  # Endpoint for the WebRTC offer

if __name__ == "__main__":
    web.run_app(app, port=8080)
