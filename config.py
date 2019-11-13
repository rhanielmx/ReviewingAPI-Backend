import os

from dotenv import load_dotenv
load_dotenv(verbose=True)

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI=f"postgresql+psycopg2://{os.getenv('SQLALCHEMY_DATABASE_URI')}" 
    #SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY= os.getenv('JWT_SECRET_KEY') or 'super-secret'
    JWT_BLACKLIST_ENABLED = True
    CORS_HEADERS = 'Content-Type'
