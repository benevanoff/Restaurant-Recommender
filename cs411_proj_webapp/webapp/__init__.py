from flask import Flask
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

def fetch_bar() -> dict:
    conn = db.connect()
    query_results = conn.execute("Select * from cs411_proj_data.Bar;").fetchall()
    conn.close()
    bar_list = []
    for result in query_results:
        item = {
            "id": result[0],
            "res_name": result[1],
            "price_level": result[2],
            "address": result[5]
        }
        bar_list.append(item)
    return bar_list

app = Flask(__name__)
app.config.from_object(Config)
db = init_db()

from webapp import routes
