# final-compre/config/config.py
import os
from config.Paths import SECRET_KEY, SQLALCHEMY_DATABASE_URI

class Config:
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = SECRET_KEY