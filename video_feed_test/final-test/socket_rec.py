import os
import shutil
import socket
import cv2
import numpy as np
import time

HOST = '127.0.0.1'
PORT = 50505
frame_dir = "saved_frames"
shutil.rmtree(frame_dir, ignore_errors=True) # --------uncmt to stop append mode 
os.makedirs(frame_dir, exist_ok=True)
FPS = 1 / 45

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST, PORT))
print('Socket bind complete')

s.listen(10)
print('Socket now listening')
data = None
conn, addr = s.accept()
frame_count = 0
while True:
    if data is not None:
        frame_count+=1
        data = conn.recv(8192)
        nparr = np.fromstring(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cam_frame_path = os.path.join(frame_dir, f"{frame_count}.jpg") 
        cv2.imwrite(cam_frame_path, frame)    
        # cv2.imshow('frame', frame)
        time.sleep(FPS)


# client-sender---------------------------------------------------------------------------------
# import socket

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect(('127.0.0.1', 50505))        
#                     sock.sendall(byte_im)                    
