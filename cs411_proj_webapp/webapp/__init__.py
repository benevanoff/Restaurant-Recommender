from flask import Flask
from config import Config
import sqlalchemy
import os

def init_db():
    pool = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL(
                drivername="mysql+pymysql",
                username= os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWD"),
                database=os.environ.get("DB_NAME"),
                host= os.environ.get("DB_HOST")
            )
        )
    return pool

app = Flask(__name__)
app.config.from_object(Config)
db = init_db()

from webapp import routes
