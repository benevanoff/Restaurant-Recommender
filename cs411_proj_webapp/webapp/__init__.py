from flask import Flask
from flask_session import Session
from config import Config
from yaml import load, Loader
import sqlalchemy
import os

def init_db():
    if os.environ.get('GAE_ENV') != 'standard':
        variables = load(open("app.yaml"), Loader = Loader)
        env_variables = variables['env_variables']
        for var in env_variables:
            os.environ[var] = env_variables[var]

    pool = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL(
                drivername="mysql+pymysql",
                username= os.environ.get("MYSQL_USER"),
                password=os.environ.get("MYSQL_PASSWORD"),
                database=os.environ.get("MYSQL_NAME"),
                host= os.environ.get("MYSQL_HOST")
            )
        )
    return pool

app = Flask(__name__)
app.config.from_object(Config)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = init_db()


from webapp import routes
