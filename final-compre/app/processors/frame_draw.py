# final-compre/app/processors/frame_draw.py
import cv2
from config.Paths import FACE_REC_TH

def Drawing_on_frame(frame, box, landmarks, subject, color, probability, draw_lan=False):
    """
    Function to process the frame before sending it to the client.
    You can add your own frame processing logic here (e.g., recognition, drawing).
    """

    cv2.rectangle(frame, (box['x_min'], box['y_min']), 
                        (box['x_max'], box['y_max']), color, 1)
    
    cv2.putText(frame, str(int(probability * 100)), (box['x_min']+5, box['y_min'] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
    # cv2.putText(frame, subject, (box['x_min']+5, box['y_min'] - 15),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
    if draw_lan:
        # Draw landmarks
        colors = [(0, 255, 0), (0, 0, 255), (0, 0, 255), (0, 255, 0), (0, 0, 255)]
        # colors = [(0, 0, 255), (0, 255, 255), (255, 0, 255), (0, 255, 0), (255, 0, 0)]
        for ((x,y), color) in zip(landmarks, colors):
            # print(f"land is {(int(x), int(y))}, type {type((int(x), int(y)))}")
            cv2.circle(frame, (int(x), int(y)), 2, color, -1)
    return frame

# def draw_detections(image, results, vis_thres=0.6):
#     """Draw bounding boxes and landmarks on the image."""
#     for result in results:
#         box = result["box"]
#         confidence = result["confidence"]
#         landmarks = result["landmarks"]

#         if confidence < vis_thres:
#             continue  # Skip detections with low confidence

#         # Draw bounding box
#         cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

#         # Draw landmarks
#         colors = [(0, 0, 255), (0, 255, 255), (255, 0, 255), (0, 255, 0), (255, 0, 0)]
#         for (point, color) in zip(landmarks, colors):
#             cv2.circle(image, point, 2, color, 4)

#     return image
