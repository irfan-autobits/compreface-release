# final-compre/app/models/model.py
from datetime import datetime
import pytz
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Helper function to get current UTC time with timezone
def get_current_time_in_timezone():
    return datetime.now(pytz.utc)

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String(50), nullable=False)
    det_face = db.Column(db.Text, nullable=False)
    person = db.Column(db.String(100), nullable=False)
    similarity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=get_current_time_in_timezone)

    def __repr__(self):
        return f"<Detection {self.camera_name}, {self.detected_face}>"
    
class Camera_list(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String(50), nullable=False)
    camera_url = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Camera_list {self.camera_name}, {self.camera_url}>"
    
class Face_recog_User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"
    