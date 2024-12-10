import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Get environment variables for database connection
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("postgres_port", "6432")

# REC_TABLE = os.getenv("REC_TABLE")
# Construct the database URL
logger.debug(f"""POSTGRES_USER={POSTGRES_USER}, 
             POSTGRES_PASSWORD={POSTGRES_PASSWORD}, 
             POSTGRES_DB={POSTGRES_DB}, 
             POSTGRES_HOST={POSTGRES_HOST}""")

# DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"


metadata = MetaData()

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class RecognitionResult(Base):
    __tablename__ = 'RecognitionResult'
    id = Column(Integer, primary_key=True, autoincrement=True)
    camera = Column(Text)
    person = Column(Text)
    accuracy = Column(Text)
    image = Column(Text)
    time = Column(DateTime(timezone=True))

Base.metadata.create_all(engine)

class DatabaseManager:
    def __init__(self):
        self.session = Session()

    async def save_results(self, results):
        batch = []
        for result in results:
            if result['subjects']:
                subject = result['subjects'][0]
                batch.append({
                    "camera": result['camera'],
                    "person": subject['subject'],
                    "accuracy": f"{subject['similarity'] * 100:.0f}%",
                    "image": result['image'],
                    "time": datetime.now()
                })
        self.session.bulk_insert_mappings(RecognitionResult, batch)
        self.session.commit()

    def close(self):
        self.session.close()
