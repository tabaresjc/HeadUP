import os
from flask import Flask
from storm.locals import *
from config import STORM_DATABASE_URI

app = Flask(__name__)
app.config.from_object('config')
database = create_database(STORM_DATABASE_URI)
store = Store(database)

from app import views