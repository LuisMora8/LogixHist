from db_models import Device, Tag, Point, IntegerPoint, FloatPoint, StringPoint, BoolPoint
from flask import current_app


def tag_value_query(tag: Tag) -> Point:
    """
    Query the last point of the given tag

    """
    with current_app.app_context():
        if tag.data_type == 'int':
            return IntegerPoint.query.filter_by(tag_id=tag.tag_id).last()
        elif tag.data_type == 'float':
            return FloatPoint.query.filter_by(tag_id=tag.tag_id).last()
        elif tag.data_type == 'string':
            return StringPoint.query.filter_by(tag_id=tag.tag_id).last()
        elif tag.data_type == 'bool':
            return BoolPoint.query.filter_by(tag_id=tag.tag_id).last()


# def get_all_device_tags(device: Device):

#     available_tags = {
#         'bool': [],
#         'int': [],
#         'float': [],
#         'string': []
#     }

#     with PLC(device.ip_address) as comm:
#         tags = comm.GetTagList()
#         # Organize available tags by data types (bools, ints, floats, strings)
#         for tag in tags.Value:
#             if tag.DataType == 'BOOL':
#                 available_tags['bool'].append(tag.TagName)
#             elif tag.DataType == 'SINT' or tag.DataType == 'INT' or tag.DataType == 'DINT':
#                 available_tags['int'].append(tag.TagName)
#             elif tag.DataType == 'REAL':
#                 available_tags['float'].append(tag.TagName)
#             elif tag.DataType == 'STRING':
#                 available_tags['string'].append(tag.TagName)

#     return available_tags
