import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display
import cv2

src = 'rtsp://autobits:Autobits@123@192.168.1.204:554'
src1 = 'rtsp://autobits:Autobits@1234@192.168.1.202:554'
st = "rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c4/s0/live"
cap = cv2.VideoCapture(st)

if not cap.isOpened():
    print("Failed to open RTSP stream")
else:
    print("RTSP stream opened successfully")

# Try capturing a frame
ret, frame = cap.read()

if ret:
    print("Frame captured successfully")
    cv2.imshow('RTSP Stream Test', frame)
    cv2.waitKey(0)
else:
    print("Failed to capture frame")

cap.release()
cv2.destroyAllWindows()
