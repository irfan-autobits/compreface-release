import cv2
import face_recognition
from deepface import DeepFace

# Initialize the webcam
video_capture = cv2.VideoCapture(0)

# Load a sample image and learn how to recognize it
known_image = face_recognition.load_image_file("irfan.png")
known_face_encoding = face_recognition.face_encodings(known_image)[0]

# Create an array of known face encodings and their names
known_face_encodings = [known_face_encoding]
known_face_names = ["irfan"]

while True:
    # Grab a single frame from the video feed
    ret, frame = video_capture.read()

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (used by OpenCV) to RGB (used by face_recognition)
    rgb_frame = small_frame[:, :, ::-1]

    # Find all face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Loop over each detected face
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Use DeepFace for more accurate face recognition
        face_crop = frame[top*4:bottom*4, left*4:right*4]  # Scale to original frame size

        # Check the face using DeepFace and compare with known faces
        try:
            result = DeepFace.find(img_path=face_crop, db_path="known_faces_db/", model_name='VGG-Face', enforce_detection=False)

            if len(result) > 0:
                name = result['identity'][0].split('/')[-1].replace('.jpg', '')
            else:
                name = "Unknown"
        except:
            name = "Unknown"

        # Scale back the face locations to the original frame size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Label the face with the name
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the frame
    cv2.imshow('Video', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
video_capture.release()
cv2.destroyAllWindows()