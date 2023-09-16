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


''' API Endpoints'''


# Home Page
@app.route('/')
def index():
    admin_url = url_for('admin.index')
    return redirect(admin_url)


# Create Device
@app.route('/create/device/<devicename>', methods=['POST'])
def create_device(devicename):
    # Get parameters
    ip_address = request.args.get('ip_address')
    slot = request.args.get('slot')
    device_type = request.args.get('type')
    route = request.args.get('route')
    connection_size = request.args.get('connection_size')
    socket_timeout = request.args.get('socket_timeout')

    if slot is None:
        slot = 0  # The processor slot is not specified, an integer argument is needed

    # Add new device to database
    device = Device(device_name=devicename, ip_address=ip_address,
                    processor_slot=slot, device_type=device_type, route=route, connection_size=connection_size, socket_timeout=socket_timeout)
    db.session.add(device)
    db.session.commit()


# Create Tag
@app.route('/create/tag/<tag_name>/<device_name>', methods=['POST'])
def create_tag(tag_name, device_name):
    # Get parameters
    device_tag_name = request.args.get('device_tag_name')
    data_type = request.args.get('data_type')
    description = request.args.get('description')
    deadband = request.args.get('deadband')

    # Get device object from database
    device = Device.query.filter_by(device_name=device_name).first()

    # Add new tag to database
    tag = Tag(device=device, tag_name=tag_name, device_tag_name=device_tag_name, data_type=data_type,
              description=description, deadband=deadband)
    db.session.add(tag)
    db.session.commit()


''' Attempt to reconnect to database in case of race issue (when starting for first time) '''


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


''' Driver Code '''
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
