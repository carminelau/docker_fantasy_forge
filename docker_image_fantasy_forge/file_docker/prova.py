from flask import Flask, request, jsonify, send_file,render_template
from pymongo import MongoClient
import gridfs
import os
from io import BytesIO
from flask_cors import CORS, cross_origin
import webbrowser
import threading


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Connetti a MongoDB
client = MongoClient('mongodb://127.0.0.1:27017')
#stampare i database presenti
print(client.list_database_names())
