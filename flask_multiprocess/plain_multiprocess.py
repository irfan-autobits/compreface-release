# flask_multiprocess/plain_multiprocess.py
import os
import shutil
from dotenv import load_dotenv
from flask import Flask, Response, jsonify
from multiprocessing import Process, Manager
import cv2
import time
import subprocess
import numpy as np
import signal
import psutil  # For port cleanup
from frame_check import FrameCheck
import logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()
FACE_DET_TH = float(os.getenv("FACE_DET_TH", 0.8))
FACE_REC_TH = float(os.getenv("FACE_REC_TH", 0.0))
host = os.getenv("HOST", 'http://localhost')
port = os.getenv("PORT", '8000')
api_key = os.getenv("API_KEY", '00000000-0000-0000-0000-000000000002')
print(f'FACE_DET_TH = {FACE_DET_TH}')
print(f'FACE_REC_TH = {FACE_REC_TH}')
print(f'host = {host}')
print(f'port = {port}')

os.environ['QT_QPA_PLATFORM'] = 'xcb'                        
# Create an instance of FaceRecognition

# Flask app
app = Flask(__name__)

# Shared status dictionary
manager = Manager()
camera_status = manager.dict()

def free_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for con in proc.net_connections(kind='inet'):

                if con.laddr.port == port:
                    print(f"Terminating process using port {port}: PID {proc.info['pid']}")
                    proc.terminate()
        except Exception:
            pass

# Function to process each camera stream
def process_camera(camera_id, url, status_dict):
    # face_recognition = FaceRecognition(api_key, host, port, FACE_REC_TH, FACE_DET_TH)
    frame_write = FrameCheck(api_key, host, port, FACE_REC_TH, FACE_DET_TH)

    # Start FFmpeg process
    ffmpeg_command = [
        # 'nice', '-n', '-19',
        "ffmpeg",
        "-i", url,             # Input URL
        '-vf', 'scale=960:540',
        "-f", "image2pipe",    # Output as image stream
        "-pix_fmt", "bgr24",   # Pixel format (OpenCV-compatible)
        "-vcodec", "rawvideo", # Raw video output
        "-"
    ]
    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    status_dict[camera_id] = {"status": "Initializing", "fps": 0, "frame": None}
    frame_count = 0
    start_time = time.time()

    while True:
        # Read raw frame bytes
        raw_frame = process.stdout.read(960 * 540 * 3)  # Adjust resolution (WxH)
        if not raw_frame:
            status_dict[camera_id] = {"status": "Disconnected", "fps": 0, "frame": None}
            break

        # Convert raw bytes to numpy array
        frame = np.frombuffer(raw_frame, np.uint8).reshape((540, 960, 3))

        # Measure frame processing time
        # start_time = time.time()  
        frame = frame_write.write_frame(frame,frame_count)
        # processing_time = time.time() - start_time
        # logging.info(f"Frame processing time: {processing_time} seconds")

        # Update FPS
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        status_dict[camera_id] = {"status": "Active", "fps": round(fps, 2), "frame": frame}

    process.terminate()


def terminate_processes(processes):
    for p in processes:
        if p.is_alive():
            logging.info(f"Terminating process: {p.pid}")
            p.terminate()
            p.join()
    logging.info("All processes terminated.")

@app.route('/camera/<int:camera_id>')
def video_feed(camera_id):
    def generate():
        while True:
            frame = camera_status[camera_id].get("frame")
            # frame = camera_status.get(camera_id, {}).get("frame")
            if frame is not None:
                # Convert the frame to JPEG
                ret, jpeg_frame = cv2.imencode('.jpg', frame)
                if ret:
                    # Yield frame as JPEG in multipart/x-mixed-replace format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame.tobytes() + b'\r\n')
            time.sleep(0.1)  # Reduce load when no new frame is available
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Flask route to get camera statuses
@app.route('/status')
def get_status():
    # Prepare status data without frames
    status_data = {camera_id: {"status": data["status"], "fps": data["fps"]} 
                   for camera_id, data in camera_status.items()}
    return jsonify(status_data)


if __name__ == '__main__':
    # Handle termination signals
    def handle_exit(signum, frame):
        print("Termination signal received. Cleaning up...")
        terminate_processes(processes)
        print("Cleanup complete. Exiting.")
        exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # camera_sources = {
    #     1: "rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c11/s0/live",
    #     2: "rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c12/s0/live"
    # }
    camera_sources = {
        1: "rtsp://autobits:Autobits@123@192.168.1.203:554",
        2: "rtsp://autobits:Autobits@1234@192.168.1.202:554",
        3: "rtsp://autobits:Autobits@123@192.168.1.201:554",
        4: "rtsp://autobits:Autobits@123@192.168.1.204:554"
    }
    

    # Free the port if in use
    free_port(5000)

    # Start camera processes
    processes = []
    for camera_id, url in camera_sources.items():
        p = Process(target=process_camera, args=(camera_id, url, camera_status))
        p.start()
        processes.append(p)

    try:
        app.run(host='0.0.0.0', port=5001, threaded=True, debug=False)
    finally:
        terminate_processes(processes)
