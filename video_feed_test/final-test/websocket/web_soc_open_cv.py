import cv2
import base64
import asyncio
from aiohttp import web

# WebSocket handler
async def video_feed(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Open the video capture
    cap = cv2.VideoCapture(0)  # Use 0 for the default webcam

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)

            # Convert to base64
            frame_b64 = base64.b64encode(buffer).decode('utf-8')

            # Send frame over WebSocket
            await ws.send_str(frame_b64)

            # Sleep to control frame rate
            await asyncio.sleep(0.03)  # ~30 FPS

    except asyncio.CancelledError:
        pass
    finally:
        cap.release()

    return ws

# Set up the app and route
app = web.Application()
app.router.add_get('/ws', video_feed)

# Run the server
web.run_app(app, port=8080)
