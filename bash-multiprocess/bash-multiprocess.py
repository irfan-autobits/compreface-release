# bash-multiprocess/bash-multiprocess.py
from datetime import datetime
import json
import sys
from flask import Flask, jsonify
from multiprocessing import Manager, Process
import os
import time
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CAMERA_SOURCES = os.getenv("CAMERA_SOURCES", "{}")

# Shared dictionary to store camera statuses
manager = Manager()
status_dict = manager.dict()

# Function to simulate running a camera process
def run_camera(camera_id, rtsp_url, database_dir, status_dict):
    try:
        # Update status to running
        status_dict[camera_id] = {"status": "running", "pid": os.getpid(), "error": None}
        print(f"Camera {camera_id} started with PID {os.getpid()}")
        # Simulate camera process or run actual ffmpeg script
        os.system(f"python3 ffmpeg-cuda-batch-compreface.py --rtsp-url {rtsp_url} --data-dir {database_dir}")
    
    except Exception as e:
        # Update status to failed on exception
        status_dict[camera_id] = {"status": "failed", "pid": None, "error": str(e)}
        print(f"Camera {camera_id} failed with error: {e}")

# Flask route to fetch camera statuses
@app.route("/status", methods=["GET"])
def get_status():
    # Convert status_dict to a regular dict for JSON serialization
    return jsonify({cam_id: data for cam_id, data in status_dict.items()})

def target_restart(restart_flag):
    target_time = "04:58:20"
    delay_time = "04:58:50"
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")

        # Check if current time matches the target time
        print(f"--===============--d:{delay_time}, c:{current_time}, t:{target_time}--===========---")
        if delay_time >= current_time <= target_time and restart_flag:
            print(f"Target time {target_time} reached. Restarting script...")
            restart_script()
            restart_flag = False
        print(f"Target time {target_time} not reached. Restarting script...? NOOO0Oo ")

        # Wait for 1 second before checking again
        time.sleep(10)

def restart_script():
    print(f"================================== Restarting **Main** script .==================================")
    processes = []
    # Start camera processes
    for cam in active_cameras:
        process = Process(target=run_camera, args=(cam["id"], cam["rtsp_url"], cam["data_dir"], status_dict))
        process.start()
        processes.append(process)

if __name__ == "__main__":
    # Define camera configurations
    print("saktiman saktiman",CAMERA_SOURCES)
    cameras = json.loads(CAMERA_SOURCES)
    active_cameras = [camera for camera in cameras if camera.get('enabled', True)]
    
    processes = []
    # Start camera processes
    for cam in active_cameras:
        process = Process(target=run_camera, args=(cam["id"], cam["rtsp_url"], cam["data_dir"], status_dict))
        process.start()
        processes.append(process)

    # try:
    #     while True:
    #         for i, process in status_dict.items():
    #             if process["status"] == "failed":
    #                 print(f"Camera {active_cameras[i]['id']} process failed. Restarting...")
    #                 process = Process(target=run_camera, args=(active_cameras[i]["id"], active_cameras[i]["rtsp_url"], active_cameras[i]["data_dir"], status_dict))
    #                 process.start()
    #                 processes[i] = process
    #         time.sleep(5)
    # except KeyboardInterrupt:
    #     for process in processes:
    #         process.terminate()

    # Start Flask app in the main thread


      
    try:
        restart_flag = True
        # Start the target_restart function in a separate process
        restart_process = Process(target=target_restart, args=(restart_flag,))
        restart_process.start()

        print("Starting Flask app...")
        app.run(host="0.0.0.0", port=5001, debug=False)
    except KeyboardInterrupt:
        print("Shutting down camera processes...")
        for process in processes:
            process.terminate()
            process.join()
        restart_process.terminate()
