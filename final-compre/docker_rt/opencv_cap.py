import cv2
cap = cv2.VideoCapture("rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c4/s0/live")  # or your RTSP URL
ret, frame = cap.read()
if ret and frame is not None:
    print("Frame captured with shape:", frame.shape)
else:
    print("Failed to capture frame")
cap.release()
