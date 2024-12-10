# instance_method/app.py
import time
import cv2
from flask import Flask, Response, jsonify, request
from Camera_ins import ThreadedCamera

app = Flask(__name__)

# Store ThreadedCamera instances in a dictionary
cameras = {
    "holl": ThreadedCamera("rtsp://autobits:Autobits@123@192.168.1.204:554"),
    "office": ThreadedCamera("rtsp://autobits:Autobits@123@192.168.1.203:554"),
    "room": ThreadedCamera("rtsp://autobits:Autobits@123@192.168.1.201:554"),
    "team": ThreadedCamera("rtsp://autobits:Autobits@1234@192.168.1.202:554"),
}

@app.route('/status', methods=['GET'])
def get_camera_status():
    if request.args.get("camera"):
        camera_name = request.args.get("camera")
        if not camera_name or camera_name not in cameras:
            return jsonify({"error": "Invalid or missing camera name"}), 400

        camera = cameras[camera_name]
        return jsonify(camera.get_status())
    else:
        res = {}
        for camera_name, camera in cameras.items():  # Use items() to get both key and value
            res[camera_name] = camera.get_status()  # Use camera_name (string) as key
        return jsonify(res)


@app.route('/video_feed/<camera_name>')
def video_feed(camera_name):
    if camera_name not in cameras:
        return "Camera not found", 404

    def generate_frames(camera):
        while True:
            frame = camera.get_frame()
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
    
    return Response(generate_frames(cameras[camera_name]), mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == '__main__':
    app.run(port=5001)
