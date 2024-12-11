from multiprocessing import Process
import time
import os

def run_camera(camera_id, rtsp_url, database_dir):
    # Each camera process runs independently
    os.system(f"python3 ffmpeg-cuda-batch-compreface.py --rtsp-url {rtsp_url} --data-dir {database_dir}")

if __name__ == "__main__":
    cameras = [
        # {"id": 1, "rtsp_url": "rtsp://autobits:Autobits@123@192.168.1.204:554", "data_dir": "Report_holl"},
        {"id": 2, "rtsp_url": "rtsp://autobits:Autobits@123@192.168.1.203:554", "data_dir": "Report_office"},
        # {"id": 3, "rtsp_url": "rtsp://autobits:Autobits@123@192.168.1.201:554", "data_dir": "Report_room"},
        {"id": 4, "rtsp_url": "rtsp://autobits:Autobits@1234@192.168.1.202:554", "data_dir": "Report_team"}
    ]

    processes = []

    for cam in cameras:
        process = Process(target=run_camera, args=(cam["id"], cam["rtsp_url"], cam["data_dir"]))
        process.start()
        processes.append(process)

    try:
        while True:
            for i, process in enumerate(processes):
                if not process.is_alive():
                    print(f"Camera {cameras[i]['id']} process failed. Restarting...")
                    process = Process(target=run_camera, args=(cameras[i]["id"], cameras[i]["rtsp_url"], cameras[i]["data_dir"]))
                    process.start()
                    processes[i] = process
            time.sleep(5)
    except KeyboardInterrupt:
        for process in processes:
            process.terminate()
