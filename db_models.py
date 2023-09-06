from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Flask and Database configuaration
app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://luis:developer@localhost/logixhistorian'
db = SQLAlchemy(app)


# Device Model
class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    device_name = db.Column(db.String)
    ip_address = db.Column(db.String)
    processor_slot = db.Column(db.Integer)
    device_type = db.Column(db.String, nullable=True)
    route = db.Column(db.Integer, nullable=True)
    connection_size = db.Column(db.Integer, nullable=True)
    socket_timeout = db.Column(db.Float, nullable=True)
    # Define the one-to-many relationship with tags
    tags = db.relationship("Tag", back_populates="device")

    def __init__(self, device_name, ip_address, processor_slot=0, device_type=None, route=None, connection_size=None, socket_timeout=None):
        super.__init__()
        self.device_name = device_name
        self.ip_address = ip_address
        self.processor_slot = processor_slot
        self.device_type = device_type
        self.route = route
        self.connection_size = connection_size
        self.socket_timeout = socket_timeout


# Tag Model
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    tag_name = db.Column(db.String)
    device_tag_name = db.Column(db.String)
    data_type = db.Column(db.String)
    device_type = db.Column(db.String, nullable=True)
    description = db.Column(db.String)
    # Foreign Key
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    # Establish the bidirectional relationship with devices
    device = db.relationship("Device", back_populates="tags")
    # Define the one-to-many relationship with trending points
    points = db.relationship("Point", back_populates="tag")

    def __init__(self, device, tag_name, device_tag_name, data_type=0, device_type=None, description=None):
        super.__init__()
        self.device = device
        self.tag_name = tag_name
        self.device_tag_name = device_tag_name
        self.data_type = data_type
        self.device_type = device_type
        self.description = description


""" Need to make subclasses of Points for different datatypes (Floats, Ints, Strings,...,) """
# Points Model


class Point(db.Model):
    __tablename__ = 'points'
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    value = db.Column(db.String)
    timestamp = db.Column(db.String)
    data_type = db.Column(db.String)
    # Foreign Key
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    # Establish the bidirectional relationship with tags
    tag = db.relationship("Tag", back_populates="points")

    def __init__(self, tag, value, timestamp, data_type):
        super.__init__()
        self.tag = tag
        self.value = value
        self.timestamp = timestamp
        self.data_type = data_type
        self.data_type = data_type
