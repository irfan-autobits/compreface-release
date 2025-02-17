import time
import cv2
from flask import Flask, Response
import socket
import threading
import struct
import pickle

app = Flask(__name__)
frames = {}  # Store frames for each camera

def handle_camera_connection(conn, addr, camera_id):
    global frames
    try:
        while True:
            # Receive frame size
            packed_size = conn.recv(4)
            if not packed_size:
                print(f"Connection closed for camera {camera_id}")
                break
            size = struct.unpack(">L", packed_size)[0]

            # Receive frame data
            data = b""
            while len(data) < size:
                packet = conn.recv(size - len(data))
                if not packet:
                    print(f"Partial frame received for camera {camera_id}")
                    break
                data += packet

            # Deserialize and store the frame
            frame = pickle.loads(data)
            # if frame is not None:
            #     print(f"Received frame for camera {camera_id}, shape: {frame.shape}")
            # else:
            #     print(f"Invalid frame received for camera {camera_id}")
            frames[camera_id] = frame
    except Exception as e:
        print(f"Error in camera connection for {camera_id}: {e}")
    finally:
        conn.close()


@app.route('/camera/<camera_id>')
def stream(camera_id):
    def generate():
        print(f"Streaming for camera {camera_id}")
        while True:
            if camera_id in frames and frames[camera_id] is not None:
                frame = frames[camera_id]
                print(f"Sending frame for camera {camera_id}, shape: {frame.shape}")
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                print(f"No valid frame for camera {camera_id}")
                # time.sleep(0.1)  # Avoid high CPU usage when no frames are available
    return Response(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Central server listening on {host}:{port}...")

    while True:
        conn, addr = server_socket.accept()
        # Receive camera ID from the client
        camera_id = conn.recv(1024).decode('utf-8').strip()  # Expect client to send ID on connect
        print(f"Camera connected: {camera_id}")
        threading.Thread(target=handle_camera_connection, args=(conn, addr, camera_id)).start()

if __name__ == "__main__":
    # threading.Thread(target=start_server, args=("127.0.0.1", 8000), daemon=True).start()
    start_server("127.0.0.1", 8000)
    app.run(host="0.0.0.0", port=5000)
