from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_admin import Admin

from db_models import db, Device, Tag, IntegerPoint, FloatPoint, StringPoint, BoolPoint
from admin_models import DeviceView, TagView, IntegerPointView, FloatPointView, StringPointView, BoolPointView

from dotenv import load_dotenv
import os

from retrying import retry

# Flask and Database configuaration
app = Flask(__name__)
CORS(app)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

# MacOS MySQL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://luis:developer@localhost/logixhistorian'

# Docker MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://luis:developer@mysql:3306/logixhistorian'

BASE_URL = "http://localhost:5000"


# Home Page
@app.route('/')
def index():
    admin_url = url_for('admin.index')
    return redirect(admin_url)


# Attempt to reconnect to database in case of race issue (when starting for first time)
def is_database_available():
    try:
        db.create_all()
        return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")


@retry(wait_fixed=2000, stop_max_attempt_number=30)
def wait_for_database():
    if not is_database_available():
        raise Exception("Database nto available let")


# Driver Code
if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        wait_for_database()
        db.create_all()
        admin = Admin(app)
        admin.add_view(DeviceView(Device, db.session))
        admin.add_view(TagView(Tag, db.session))
        admin.add_view(IntegerPointView(IntegerPoint, db.session))
        admin.add_view(FloatPointView(FloatPoint, db.session))
        admin.add_view(StringPointView(StringPoint, db.session))
        admin.add_view(BoolPointView(BoolPoint, db.session))
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(debug=True)
