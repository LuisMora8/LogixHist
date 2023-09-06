from flask import render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from db_models import app, db

BASE_URL = "http://127.0.0.1:5000"
CORS(app)

# Home Page


@app.route('/')
def index():
    return render_template('index.html')
