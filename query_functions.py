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


def tag_value_query(tag_name: str) -> Point:
    """
    Query the last point of the given tag

    """
    with current_app.app_context():
        tag = Tag.query.filter_by(tag_name=tag_name).first()
        if tag.data_type == 'int':
            return IntegerPoint.query.filter_by(tag_id=tag.tag_id).last()
        elif tag.data_type == 'float':
            return FloatPoint.query.filter_by(tag_id=tag.tag_id).last()
        elif tag.data_type == 'string':
            return StringPoint.query.filter_by(tag_id=tag.tag_id).last()
        elif tag.data_type == 'string':
            return BoolPoint.query.filter_by(tag_id=tag.tag_id).last()
