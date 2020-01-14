from flask import Flask

# import mysql.connector
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


from app import routes
