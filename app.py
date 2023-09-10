from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_admin import Admin

from db_models import db, Device, Tag, IntegerPoint, FloatPoint, StringPoint, BoolPoint
from admin_models import DeviceView, TagView, IntegerPointView, FloatPointView, StringPointView, BoolPointView

from dotenv import load_dotenv
import os

# Flask and Database configuaration
app = Flask(__name__)
CORS(app)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://luis:developer@localhost/logixhistorian'

BASE_URL = "http://127.0.0.1:5000"

# Home Page


@app.route('/')
def index():
    return render_template('index.html')


# Driver Code
if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        db.create_all()
        admin = Admin(app)
        admin.add_view(DeviceView(Device, db.session))
        admin.add_view(TagView(Tag, db.session))
        admin.add_view(IntegerPointView(IntegerPoint, db.session))
        admin.add_view(FloatPointView(FloatPoint, db.session))
        admin.add_view(StringPointView(StringPoint, db.session))
        admin.add_view(BoolPointView(BoolPoint, db.session))
    app.run(debug=True)
