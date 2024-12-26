# final-compre/scripts/manage_db.py
from app.models.model import db, Detection
from sqlalchemy.exc import ProgrammingError

def manage_table(purge=False, drop=False):
        try:
            if purge:
                # Delete all data if the table exists
                db.session.query(Detection).delete()
                db.session.commit()
                print("Purged all rows in the Detection table.")
            elif drop:
                db.drop_all()
                db.create_all()
                print("Dropped all the table.")
            else:
                # Ensure the table exists
                db.create_all()
                print("Created all the table if it didn't exist.")
        except ProgrammingError:
            print("The table does not exist yet.")  