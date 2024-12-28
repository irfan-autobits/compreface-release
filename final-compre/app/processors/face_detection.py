# final-compre/app/processors/face_detection.py
from integrations.Compre_Api import compreface_api
from app.processors.frame_draw import Drawing_on_frame
from app.processors.Save_Face import save_image
from app.models.model import db, Detection
from config.Paths import FACE_REC_TH
from datetime import datetime


class FaceDetectionProcessor:
    def __init__(self, camera_sources, db_session, app):
        self.camera_sources = camera_sources
        self.db_session = db_session
        self.app = app  # Store the Flask app instance


    def process_frame(self, frame, cam_name):
        results = compreface_api(frame)
        if results:
            print(f"result on one frame are ::::::::::: {len(results)}")
            for result in results:
                box = result.get('box')
                subject = result.get('subjects')[0]['subject']
                similarity = result.get('subjects')[0]['similarity']
                
                is_unknown = False
                if similarity >= float(FACE_REC_TH):
                    color = (0, 255, 0)  # Green color for text                        
                else:
                    color = (0, 0, 255)
                    subject = f"Un_{subject}"
                    is_unknown = True

                                            
                frame = Drawing_on_frame(frame, box, subject, color)  
                face_path = save_image(frame, cam_name, box, subject, similarity, is_unknown)

                # Use the app context explicitly
                with self.app.app_context():
                    detection = Detection(
                        camera_name=cam_name, 
                        det_face=face_path,
                        person = subject, 
                        similarity=similarity,
                        timestamp=datetime.now()
                    )
                    self.db_session.add(detection)
                    # self.db_session.commit()

                    # Commit every 10 detections
                    if len(self.db_session.new) % 10 == 0:
                        self.db_session.commit()

        return frame
