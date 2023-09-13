from db_models import Device, Tag, Point, IntegerPoint, FloatPoint, StringPoint, BoolPoint
from flask import current_app


def device_query():
    """
    Query all devices for admin page

    """
    with current_app.app_context():
        return Device.query.all()

# Query for selecting a tag in Admin when making a Point


def tag_query(data_type: str):
    """
    Query all tags for admin page

    """
    with current_app.app_context():
        return Tag.query.filter_by(data_type=data_type).all()
