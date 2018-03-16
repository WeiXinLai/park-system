from flask import Flask
import logging
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.debug = True
handler = logging.FileHandler('/home/BigWhile/park-system/logs/uwsgi/park.log'
)
app.logger.addHandler(handler)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:laiweixin@localhost:3306/test?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db = SQLAlchemy(app)
