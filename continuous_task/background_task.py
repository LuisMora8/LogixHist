from pylogix import PLC
from flask import Flask
from db_models import db, Device, Tag, IntegerPoint, FloatPoint, StringPoint, BoolPoint
from app.query_functions import tag_value_query

app = Flask(__name__)
database_uri = 'mysql://luis:developer@mysql:3306/logixhistorian'
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db.init_app(app)

cached_devices = []
cached_tags = {}


def look_for_new_devices():
    # Read data from the database
    with app.app_context():
        devices = Device.query.all()
        # Update cached devices as needed
        if cached_devices is not devices:
            cached_devices = devices


def look_for_new_tags():
    # Read data from the database
    with app.app_context():
        tags = Tag.query.all()
        # Update cached devices as needed
        if cached_tags is not tags:
            cached_tags = tags


def get_all_device_tags(device: Device):
    """
    Looks up the available tags from a given device and organizes based off data types.

    Args:
        device (Device): A device object that has an IP Address

    Returns:
        dict: The available tags
        {
          'bool': [],
          'int': [],
          'float': [],
          'string': []
        }

    Notes:
        Any data types that are not ints, bools, floats, or strings will be ignored (UDTS, AB:1756_OF8_Float, etc..)
    """

    available_tags = {
        'bool': [],
        'int': [],
        'float': [],
        'string': []
    }

    with PLC(device.ip_address) as comm:
        tags = comm.GetTagList()
        # Organize available tags by data types (bools, ints, floats, strings)
        for tag in tags.Value:
            if tag.DataType == 'BOOL':
                available_tags['bool'].append(tag.TagName)
            elif tag.DataType == 'SINT' or tag.DataType == 'INT' or tag.DataType == 'DINT':
                available_tags['int'].append(tag.TagName)
            elif tag.DataType == 'REAL':
                available_tags['float'].append(tag.TagName)
            elif tag.DataType == 'STRING':
                available_tags['string'].append(tag.TagName)

    return available_tags


def monitor_tags(device: Device, tags: [Tag]):
    """
    Brief description of what the function does.

    Args:
        arg1 (type): Description of arg1.
        arg2 (type, optional): Description of arg2 with a default value (if applicable).
        *args: Description of any additional positional arguments (if applicable).
        **kwargs: Description of any additional keyword arguments (if applicable).

    Returns:
        return_type: Description of what the function returns.

    Raises:
        ExceptionType: Description of the exceptions raised by the function (if applicable).

    Notes:
        Any additional notes or details about the function.
    """

    with PLC(device.ip_address) as comm:

        while True:
            for tag in tags:
                # Read the tag and query the last point
                response = comm.Read(tag.device_tag_name)
                last_point = tag_value_query(tag.device_tag_name)

                if response.Value is not last_point.value:
                    print(response)
