import cv2
import argparse
import time
import os
import shutil
import numpy as np
from threading import Thread
import pandas as pd
from compreface import CompreFace
from compreface.service import RecognitionService
# from sqlalchemy import create_engine, text
from datetime import datetime

# Generate the timestamp
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
# timestamp = f"recognition_results_{timestamp}"

# Directory to store employee images
database_dir = 'Report'
# Create the main database directory if it doesn't exist
shutil.rmtree(database_dir, ignore_errors=True)
os.makedirs(database_dir, exist_ok=True)
print('created/checked database_dir')
excel_name = 'face_recognition_results.xlsx'
excel_path = os.path.join(database_dir, excel_name)
    
# postgre - - - - - - - - - - 
# from sqlalchemy import create_engine, Column, Integer, String, Text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# # Define the database URL
# DATABASE_URL = "postgresql+psycopg2://postgres:pgsqlpass@localhost:5432/postgres"

# # Create a database engine
# engine = create_engine(DATABASE_URL)

# # Define the Base class
# Base = declarative_base()

# # Define the Table schema
# class RecognitionResult(Base):
#     __tablename__ = 'recognition_results'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     age_low = Column(Integer)
#     age_high = Column(Integer)
#     gender = Column(String)
#     mask = Column(String)
#     subjects = Column(Text)  # Use Text for longer strings
#     image = Column(String)

# # Drop the table
# Base.metadata.drop_all(engine)
# print("All tables have been dropped.")

# # Create tables in the database
# Base.metadata.create_all(engine)

# # Create a session
# Session = sessionmaker(bind=engine)
# session = Session()

# # # Purge all rows from the table
# # session.query(RecognitionResult).delete()
# # session.commit()
# # print("All rows deleted from the table.")

# error [hevc @ 0x27a5140] Could not find ref with POC 3
#  - - - - - - - - - - - - - -

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--api-key", help="CompreFace recognition service API key", type=str, default='c7d5f325-7167-463a-a1f5-b973422b868e')
    # parser.add_argument("--api-key", help="CompreFace recognition service API key", type=str, default='00000000-0000-0000-0000-000000000002')
    parser.add_argument("--host", help="CompreFace host", type=str, default='http://localhost')
    parser.add_argument("--port", help="CompreFace port", type=str, default='8000')
    parser.add_argument("--rtsp", help="Use RTSP stream (True/False)", type=str, default='True')
    parser.add_argument("--rtsp-url", help="RTSP stream URL", type=str, default='rtsp://autobits:Autobits@123@192.168.1.204:554')

    args = parser.parse_args()
    args.rtsp = args.rtsp.lower() == 'true'
    return args

def apply_clahe(image):
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the image."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Create a CLAHE object with desired clip limit and grid size
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    # Apply CLAHE to the grayscale image
    clahe_img = clahe.apply(gray)

    # Convert back to BGR after CLAHE
    return cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2BGR)

def apply_gamma_correction(image, gamma=1.0):
    """Apply Gamma Correction to the image."""
    # Build a lookup table for gamma correction
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")

    # Apply gamma correction using the lookup table
    return cv2.LUT(image, table)
    
class ThreadedCamera:
    def __init__(self, api_key, host, port, use_rtsp, rtsp_url):
        self.active = True
        self.results = []
        self.rows = [] 

        if use_rtsp:
            self.capture = cv2.VideoCapture(rtsp_url)
        else:
            self.capture = cv2.VideoCapture(0)
        
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        compre_face: CompreFace = CompreFace(host, port, {
            "limit": 0,
            "det_prob_threshold": 0.8,
            "prediction_count": 1,
            "face_plugins": "age,gender",
            "status": False
        })

        self.recognition: RecognitionService = compre_face.init_face_recognition(api_key)

        self.FPS = 1/30

        # Start frame retrieval thread
        self.thread = Thread(target=self.show_frame, args=())
        self.thread.daemon = True
        self.thread.start()
        # File to store results
        self.excel_path = excel_path
        

    def show_frame(self):
        print("Started")
        while self.capture.isOpened():
            (status, frame_raw) = self.capture.read()
            # self.frame = cv2.flip(frame_raw, 1)

            # Apply CLAHE and Gamma Correction before processing the frame
            # processed_frame = apply_clahe(frame_raw)
            processed_frame = apply_gamma_correction(frame_raw, gamma=1.5)  # Adjust gamma value as needed
            # processed_frame = cv2.resize(processed_frame, (1270, 720))
            self.frame = processed_frame  # Use the processed frame for face detection

            if self.results:
                results = self.results
                for result in results:
                    box = result.get('box')
                    age = result.get('age')
                    gender = result.get('gender')
                    mask = result.get('mask')
                    subjects = result.get('subjects')
                    if box:

                        if subjects and subjects[0]['similarity'] >= 0.7:
                            if age:
                                age = f"Age: {age['low']} - {age['high']}"
                                cv2.putText(self.frame, age, (box['x_max'], box['y_min'] + 15),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                            if gender:
                                gender = f"Gender: {gender['value']}"
                                cv2.putText(self.frame, gender, (box['x_max'], box['y_min'] + 35),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                            if mask:
                                mask = f"Mask: {mask['value']}"
                                cv2.putText(self.frame, mask, (box['x_max'], box['y_min'] + 55),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                            subjects = sorted(subjects, key=lambda k: k['similarity'], reverse=True)
                            subject = f"Subject: {subjects[0]['subject']}"
                            similarity = f"Similarity: {subjects[0]['similarity']}"
                            cv2.putText(self.frame, subject, (box['x_max'], box['y_min'] + 75),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                            cv2.putText(self.frame, similarity, (box['x_max'], box['y_min'] + 95),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                            cv2.rectangle(img=self.frame, pt1=(box['x_min'], box['y_min']),
                                      pt2=(box['x_max'], box['y_max']), color=(0, 255, 0), thickness=1)
                        else:
                            if age:
                                age = f"Age: {age['low']} - {age['high']}"
                                cv2.putText(self.frame, age, (box['x_max'], box['y_min'] + 15),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                            if gender:
                                gender = f"Gender: {gender['value']}"
                                cv2.putText(self.frame, gender, (box['x_max'], box['y_min'] + 35),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                            if mask:
                                mask = f"Mask: {mask['value']}"
                                cv2.putText(self.frame, mask, (box['x_max'], box['y_min'] + 55),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                            subject = f"No known faces"
                            cv2.putText(self.frame, subject, (box['x_max'], box['y_min'] + 75),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                            cv2.rectangle(img=self.frame, pt1=(box['x_min'], box['y_min']),
                                      pt2=(box['x_max'], box['y_max']), color=(0, 0, 255), thickness=1)

            cv2.imshow('CompreFace demo', self.frame)
            time.sleep(self.FPS)

            if cv2.waitKey(1) & 0xFF == 27 or cv2.waitKey(1) & 0xFF == ord('q'):
                self.capture.release()
                cv2.destroyAllWindows()
                self.active = False

    def is_active(self):
        return self.active

    def update(self, frame_count):
        """Processes the frame and updates recognition results."""
        if not hasattr(self, 'frame'):
            return

        # Encode frame to bytes
        _, im_buf_arr = cv2.imencode(".jpg", self.frame)
        byte_im = im_buf_arr.tobytes()
        data = self.recognition.recognize(byte_im)

        # Filter recognition results
        self.results = self.filter_recognition_results(data)
        # Print filtered data for debugging
        print('Filtered data:', self.results)
        
        # Save results to Excel and save face images with the current frame_count
        self.save_results_to_excel(self.results, frame_count)

    def filter_recognition_results(self, data):
        # Filters recognition results to include only subjects with similarity >= 0.7.
        filtered_results = []
        if 'result' in data:
            for result in data['result']:
                subjects = result.get('subjects', [])
                # Keep only subjects with similarity >= 0.7
                subjects = [sub for sub in subjects if sub['similarity'] >= 0.7]
                # Keep all subjects, recognized or unrecognized
                result['subjects'] = subjects  
                filtered_results.append(result)
        return filtered_results

    def save_results_to_excel(self, results, frame_count):
        """Saves the results to an Excel file and saves the detected faces as images."""
        if results:
            for result in results:
                box = result.get('box', {})
                age = result.get('age', {})
                gender = result.get('gender', {})
                mask = result.get('mask', {})
                subjects = result.get('subjects', [])

                # Prepare subjects info
                subjects_info = ', '.join([f"{sub['subject']} ({sub['similarity']})" for sub in subjects])

                # Create row dictionary for Excel
                row = {
                    'id': frame_count,  # Use frame_count as id
                    'age_low': age.get('low'),
                    'age_high': age.get('high'),
                    'gender': gender.get('value'),
                    'mask': mask.get('value'),
                    'subjects': subjects_info
                }

                # Append row data to the list
                self.rows.append(row)

                # Save the detected face as an image
                if box:
                    # Extract face region using bounding box
                    face_image = self.frame[box['y_min']:box['y_max'], box['x_min']:box['x_max']]

                    # Define file path to save the image
                    face_image_name = f"{timestamp}_{subjects_info}_{frame_count}.jpg"
                    face_image_path = os.path.join(database_dir, face_image_name)

                    # Save the face as a JPG image
                    cv2.imwrite(face_image_path, face_image)
                    print(f"Saved detected face as: {face_image_name}")

                # Save data to PostgreSQL
                # recognition_result = RecognitionResult(
                #     age_low=age.get('low'),
                #     age_high=age.get('high'),
                #     gender=gender.get('value'),
                #     mask=mask.get('value'),
                #     subjects=subjects_info,
                #     image = f"{timestamp}_{subjects_info}_{frame_count}.jpg"
                # )
                # session.add(recognition_result)
                # session.commit()

        else:
            print('No result to save')
            
        
if __name__ == '__main__':
    args = parseArguments()
    threaded_camera = ThreadedCamera(args.api_key, args.host, args.port, args.rtsp, args.rtsp_url)

    frame_interval = 3  # Process every 3rd frame
    frame_count = 0  # Initialize frame counter
    
    while threaded_camera.is_active():
        frame_count += 1  # Increment frame counter

        # Skip frames that are not the 3rd one in sequence
        if frame_count % frame_interval != 0:
            print(f'Skip{frame_count},{frame_interval}')
            continue  # Skip this iteration and go to the next frame

        # Update the camera with the current frame count
        threaded_camera.update(frame_count)
    # Create DataFrame and save results to Excel
    df = pd.DataFrame(threaded_camera.rows)
    df.to_excel(excel_path, index=False)
    print(f"Results saved to {excel_path}")

    # Close the PostgreSQL session
    # session.close()
    # print("PostgreSQL session closed")
