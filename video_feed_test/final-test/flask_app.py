from flask import Flask, Response
from Recognition_api import ThreadedCamera  # Import your ThreadedCamera class
# from ffmpeg_cuda_batch_compreface import ThreadedCamera

app = Flask(__name__)

# Dictionary to hold camera objects
cameras = {}

@app.route('/video_feed/<cam_id>')
def video_feed(cam_id):
    def generate_frames():
        if cam_id in cameras:
            camera = cameras[cam_id]
            while True:
                frame = camera.get_frame()
                if frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                else:
                    break
        else:
            yield b'Camera not found'

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Initialize cameras with different RTSP URLs and IDs
    cameras['0'] = ThreadedCamera(src="rtsp://autobits:Autobits@123@192.168.1.203:554")
    cameras['1'] = ThreadedCamera(src="rtsp://autobits:Autobits@1234@192.168.1.202:554")

    app.run(host='0.0.0.0', port=5001, threaded=True)
