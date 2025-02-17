import logging
import cv2
import base64
import asyncio
from aiohttp import web
from VideoCapture import VideoStream

# WebSocket handler
async def video_feed(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    src  = "rtsp://autobits:Autobits@123@192.168.1.204:554"
    FPS = 1 / 45 # ~45 FPS
    FPS_MS = int(FPS * 1000)     
    # Open the video capture instance
    in_cam = VideoStream(src)  
    in_cam.start()

    try:
        while True:
            frame = in_cam.read()
            if frame is not None:
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)

                # Convert to base64
                frame_b64 = base64.b64encode(buffer).decode('utf-8')

                # Send frame over WebSocket
                await ws.send_str(frame_b64)

                # Sleep to control frame rate
                await asyncio.sleep(FPS)  
            else:
                logging.warning(f"Frame is None for camera ")                 

    except asyncio.CancelledError:
        pass
    finally:
        in_cam.stop()

    return ws

# Set up the app and route
app = web.Application()
app.router.add_get('/ws', video_feed)

# Run the server
web.run_app(app, port=8080)
