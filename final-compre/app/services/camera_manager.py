# final-compre/app/services/camera_manager.py
from datetime import datetime 
import json
from app.models.model import Camera_list, db
from flask import current_app
from app.processors.VideoCapture import VideoStream  
from config.Paths import frame_lock, vs_list, cam_sources
from config.logger_config import cam_stat_logger 

def Default_cameras():
    """API endpoint to add default cameras"""
    try:
        global cam_sources
        # with current_app.app_context():
        for cam_name, source in cam_sources.items():
            new_camera = Camera_list(camera_name=cam_name, camera_url=source)
            db.session.add(new_camera)
            print(f"Default camera {cam_name} added successfully")
        db.session.commit()
        with frame_lock:
            for cam_name, source in cam_sources.items():
                vs_list[cam_name] = VideoStream(src=source)
                vs_list[cam_name].start()
        return {'message' : 'Default cameras added successfully'}, 200
    except Exception as e:
        db.session.rollback()
        return {'error' : str(e)}, 500

def Add_camera(camera_name,camera_url):
    """API endpoint to add a camera"""
    new_camera = Camera_list(camera_name=camera_name, camera_url=camera_url)
    global vs_list, cam_sources
    try:
        global cam_sources
        with current_app.app_context():
            db.session.add(new_camera)
            db.session.commit()
            with frame_lock:
                cam_sources[camera_name] = camera_url
                responce, status = Start_camera(camera_name)
                timestamp = datetime.now()
                cam_stat_logger.info(f"Camera {camera_name} added successfully at {timestamp}")
                # responce, status = {'message' : f"Camera {camera_name} added successfully"}, 200
            return responce, status
    except Exception as e:
        db.session.rollback()
        cam_stat_logger.error(f"Failed to add camera {camera_name}: {str(e)}")
        return {'error' : str(e)}, 500
    
def Remove_camera(camera_name,camera_url):
    """API endpoint to remove a camera"""
    global vs_list, cam_sources
    try:
        with current_app.app_context():
            camera = Camera_list.query.filter_by(camera_name=camera_name, camera_url=camera_url).first()
            if camera:
                db.session.delete(camera)
                db.session.commit()
                with frame_lock:
                    responce, status = Stop_camera(camera_name)
                    timestamp = datetime.now()
                    cam_stat_logger.info(f"Camera {camera_name} removed successfully at {timestamp}")
                    # responce, status = {'message' : f"Camera {camera_name} removed successfully"}, 200
                    if camera_name in cam_sources:
                        del cam_sources[camera_name]
                return responce, status
            else:
                return {'error' : f'Camera {camera_name} not found'}, 404
    except Exception as e:
        db.session.rollback()
        cam_stat_logger.error(f"Failed to Remove camera {camera_name}: {str(e)}")
        return {'error' : str(e)}, 500

def Start_camera(camera_name):
    """API endpoint to start a camera feed"""
    global vs_list, cam_sources
    if camera_name in cam_sources:
        if camera_name in vs_list:
            return {'message' : f'Video feed already started for {camera_name}'}, 200
        else:
            vs_list[camera_name] = VideoStream(src=cam_sources[camera_name])
            vs_list[camera_name].start()
            timestamp = datetime.now()
            cam_stat_logger.info(f"Camera {camera_name} started successfully at {timestamp}")
            return {'message' : f'Video feed started for {camera_name}'}, 200
    else:
        return {'error' : f'Camera {camera_name} not found'}, 404

def Stop_camera(camera_name):
    """API endpoint to stop a camera feed"""
    global vs_list
    if camera_name in vs_list:
        vs_list[camera_name].stop()
        del vs_list[camera_name]
        timestamp = datetime.now()
        cam_stat_logger.info(f"Camera {camera_name} stoped successfully at {timestamp}")
        return {'message' : f'Video feed stopped for {camera_name}'}, 200
    else:
        return {'error' : f'Camera {camera_name} not found'}, 404