from db_models import Device, Tag
from flask import current_app

# Query for selecting a device in Admin when making a Tag


def device_query():
    with current_app.app_context():
        return Device.query.all()

# Query for selecting a tag in Admin when making a Point


def tag_query(data_type: str):
    with current_app.app_context():
        return Tag.query.filter_by(data_type=data_type).all()
