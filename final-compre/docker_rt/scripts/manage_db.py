# final-compre/scripts/manage_db.py
from app.models.model import db, Detection, Camera_list, Face_recog_User
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from config.logger_config import cam_stat_logger , console_logger, exec_time_logger

def manage_table(purge=False, drop=False, spec=False, doc=False):
    try:
        if purge:
            # Delete all data if the table exists
            db.session.query(Detection).delete()
            db.session.commit()
            print("Purged all rows in the Detection table.")
        elif spec:
            # Drop the specific table
            Camera_list.__table__.drop(db.engine)
            # db.session.commit()
            Face_recog_User.__table__.drop(db.engine)
            # Detection.__table__.drop(db.engine)
            db.session.commit()
            db.create_all()
            print("Dropped everything apart from Detection.")
        elif drop:
            db.drop_all()
            db.create_all()
            print("Dropped all the table.")
        elif doc:
            # Delete all data if the table exists
            db.session.query(Camera_list).delete()
            db.session.commit()
            db.create_all()
            console_logger.debug(f"manage called")       

            print("Purged all rows in the Detection table.")
        else:
            # Ensure the table exists
            db.create_all()
            print("Created all the table if it didn't exist.")
    except ProgrammingError:
        print("The table does not exist yet.")  
