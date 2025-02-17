# video_feed_test/final-test/open-multi-check.py
import logging
from multiprocessing import Process
import os
import shutil
from threading import Thread
import time
logging.basicConfig(level=logging.INFO)
import cv2
import json
from VideoCapture import VideoStream
frame_dir = "saved_frames"
shutil.rmtree(frame_dir, ignore_errors=True) # --------uncmt to stop append mode 
os.makedirs(frame_dir, exist_ok=True)

def detection_video_stream(cam_id, camera_url):
    # Create VideoStream instances for each camera
    camera = VideoStream(camera_url)
    camera.start()
    frame_count = 0
    # FPS = 1 / 25
    # FPS_MS = int(FPS * 1000)    

    cam_frame_dir = os.path.join(frame_dir, cam_id) 
    os.makedirs(cam_frame_dir, exist_ok=True)

    try:
        # Display frames from each camera in separate windows
        while camera:
            # start_time = time.time()
            frame = camera.read()
            if frame is not None:
                # elapsed_time = time.time() - start_time
                frame_count+=1
                # fps = frame_count / elapsed_time
                # fps = 1 / elapsed_time if elapsed_time > 0 else 0  # Avoid division by zero
                # cam_frame_path = os.path.join(cam_frame_dir, f"{frame_count}_{cam_id}.jpg") 
                # cv2.imwrite(cam_frame_path, frame)
                cv2.imshow('frame',frame)
                # status_dict[cam_id] = {"status": "Active", "fps": round(fps, 2), "frame": frame}
                logging.info(f"frame: {frame_count} ~ {cam_id}")
                # time.sleep(FPS)

            else:
                logging.warning(f"Frame not available for camera {cam_id}")

    except Exception as e:
        logging.error(f"Error in camera thread {cam_id}: {e}")
    finally:
        camera.stop()
        logging.info(f"Stopped camera {cam_id}")              

if __name__ == '__main__':
    # Define a list of RTSP URLs
    camera_urls = {
        'holl': 'rtsp://autobits:Autobits@123@192.168.1.204:554',
        # 'office': 'rtsp://autobits:Autobits@123@192.168.1.203:554',
        # 'room':'rtsp://autobits:Autobits@123@192.168.1.201:554',
        # 'team':'rtsp://autobits:Autobits@1234@192.168.1.202:554'
    }

    try:
        frames_dict={}
        status_dict = {}
        processes = []
        # Start camera processes
        for cam_id, camurl in camera_urls.items():
            # process = Process(target=detection_video_stream, args=(cam_id,camurl))
            # process.daemon = True
            # process.start()
            # processes.append(process)
            detection_video_stream(cam_id,camurl)
        

    except KeyboardInterrupt:
        print("Shutting down camera processes...")
        for process in processes:
            process.terminate()
            process.join()        




