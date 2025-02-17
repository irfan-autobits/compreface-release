# database.py
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Database configuration
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"
engine = create_engine(DATABASE_URL, echo=False)
# engine = create_engine(
#     DATABASE_URL,
#     poolclass=QueuePool,
#     pool_size=10,          # Number of connections in the pool
#     max_overflow=20,       # Additional connections when pool is full
#     pool_timeout=30,       # Seconds to wait before giving up on a connection
#     pool_recycle=3600,     # Seconds after which connections are recycled
# )

# Base model
Base = declarative_base()

# Database session
Session = sessionmaker(bind=engine)

# RecognitionResult Model
class RecognitionResult(Base):
    __tablename__ = 'Hathi_recognition'
    id = Column(Integer, primary_key=True, autoincrement=True)
    camera = Column(Text)
    person = Column(Text)
    accuracy = Column(Text)
    image = Column(Text)
    time = Column(DateTime(timezone=True))


# Create tables
def init_db():
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


    # # Function to save recognition results to the database
    # def save_recognition_results(results, camera_name, session):
    #     batch = []
    #     for result in results:
    #         batch.append(RecognitionResult(
    #             camera=camera_name,
    #             person=result['person'],
    #             accuracy=result['accuracy'],
    #             image=result['image'],
    #             time=datetime.now()
    #         ))
    #     session.bulk_save_objects(batch)
    #     session.commit()
