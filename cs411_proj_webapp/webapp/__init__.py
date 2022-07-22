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

app = Flask(__name__)
app.config.from_object(Config)
db = init_db()

conn = db.connect()
results = conn.execute("SELECT * FROM cs411_proj_data.Bar").fetchall()
print([x for x in results])
conn.close()

from webapp import routes
