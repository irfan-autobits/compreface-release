import multiprocessing
import queue
import subprocess
import sys
from Recognitionst import run_rtsp_stream
import cv2
        
def run_multiple_rtsp_streams(rtsp_urls):
    frame_queues = [queue.Queue() for _ in rtsp_urls]  # One queue per stream
    processes = []

    for rtsp_url, frame_queue in zip(rtsp_urls, frame_queues):
        # Start a new process for each RTSP stream
        p = multiprocessing.Process(target=run_rtsp_stream, args=(rtsp_url, frame_queue))
        processes.append(p)
        p.start()

    # Main process retrieves frames from each stream
    while True:
        for i, frame_queue in enumerate(frame_queues):
            if not frame_queue.empty():
                frame = frame_queue.get()
                print('got_frames')
                # Display the frame from each stream (use stream names or indexes)
                cv2.imshow(f"Stream {i}", frame)
                cv2.waitKey(1)

    for p in processes:
        p.join()

if __name__ == '__main__':
    rtsp_urls = [
        'rtsp://autobits:Autobits@123@192.168.1.204:554',
        'rtsp://autobits:Autobits@123@192.168.1.203:554',
    ]

    run_multiple_rtsp_streams(rtsp_urls)