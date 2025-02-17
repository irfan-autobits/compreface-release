# video_feed_test/final-test/open-multi-pure.py
import logging
import os
import shutil
import time
logging.basicConfig(level=logging.INFO)
import cv2
import json
from VideoCapture import VideoStream
# from VideoStremer import VideoStream
frame_dir = "saved_frames"
shutil.rmtree(frame_dir, ignore_errors=True)
os.makedirs(frame_dir, exist_ok=True)

def detection_video_stream(camera_urls):
    # Create VideoStream instances for each camera
    cameras = [VideoStream(url) for url in camera_urls]

    # Start reading frames from each camera
    for camera in cameras:
        camera.start()
        frame_count = 0
        FPS = 1 / 45
        FPS_MS = int(FPS * 1000) 

    cam_frame_dir = os.path.join(frame_dir, f"{cameras.index(camera)+1}") 
    os.makedirs(cam_frame_dir, exist_ok=True)
    try:
        # Display frames from each camera in separate windows
        while cameras:
            for i, camera in enumerate(cameras):
                frame = camera.read()
                if frame is not None:
                    # cv2.imshow(f"Camera {i+1}", frame)
                    # cam_frame_path = os.path.join(cam_frame_dir, f"{frame_count}_{cam_id}.jpg") 
                    # cv2.imwrite(cam_frame_path, frame)
                    # _, im_buf_arr = cv2.imencode(".jpg", frame)
                    # byte_im = im_buf_arr.tobytes()
                    logging.info(f'got frames for {cameras.index(camera)+1}')
                    # status_dict[cam_id] = {"status": "Active", "fps": round(fps, 2), "frame": frame}
                    logging.info(f"Camera {cameras.index(camera)+1}")
                    time.sleep(FPS)
                else:
                    logging.warning(f"Frame is None for camera {cameras.index(camera)+1}")              

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) == ord('q'):
                break

    except Exception as e:
        logging.error(f"Error in camera thread {cameras.index(camera)+1}: {e}")
    finally:
        for camera in cameras:
            camera.stop()
            logging.info(f"Stopped camera {cameras.index(camera)+1}") 
        cv2.destroyAllWindows()

if __name__ == '__main__':
    
    # Define a list of RTSP URLs
    camera_urls = [
        'rtsp://autobits:Autobits@123@192.168.1.204:554',
        # 'rtsp://autobits:Autobits@123@192.168.1.203:554',
        # 'rtsp://autobits:Autobits@123@192.168.1.201:554',
        # 'rtsp://autobits:Autobits@1234@192.168.1.202:554'
    ]
    detection_video_stream(camera_urls)