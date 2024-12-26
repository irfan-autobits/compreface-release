# final-compre/app/processors/frame_draw.py
import cv2
from config.Paths import FACE_REC_TH

def Drawing_on_frame(frame, box, subject, color):
    """
    Function to process the frame before sending it to the client.
    You can add your own frame processing logic here (e.g., recognition, drawing).
    """

    cv2.rectangle(frame, (box['x_min'], box['y_min']), 
                        (box['x_max'], box['y_max']), color, 1)
    cv2.putText(frame, subject, (box['x_min']+5, box['y_min'] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

    return frame

