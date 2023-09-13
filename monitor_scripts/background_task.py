from pylogix import PLC
from flask import Flask
from db_models import db, Device, Tag, IntegerPoint, FloatPoint, StringPoint, BoolPoint
from query_functions import tag_value_query

app = Flask(__name__)
# MacOS MySQL
# database_uri = 'mysql://luis:developer@localhost/logixhistorian'
database_uri = 'mysql://luis:developer@mysql:3306/logixhistorian'
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db.init_app(app)

cached_devices = []
cached_tags = {}


def look_for_new_devices(cached_devices):
    # Read data from the database
    with app.app_context():
        devices = Device.query.all()
        # Update cached devices as needed
        if cached_devices is not devices:
            return devices
        return cached_tags


def look_for_new_tags(cached_tags):
    # Read data from the database
    with app.app_context():
        tags = Tag.query.all()
        # Update cached devices as needed
        if cached_tags is not tags:
            return tags
        else:
            return cached_tags


def get_all_device_tags(device: Device):

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

    with PLC(device.ip_address) as comm:

        while True:
            for tag in tags:
                # Read the tag and query the last point
                response = comm.Read(tag.device_tag_name)
                last_point = tag_value_query(tag.device_tag_name)

                if response.Value is not last_point.value:
                    print(response)


# Driver Code
if __name__ == '__main__':
    cached_devices = look_for_new_devices(cached_devices)
    cached_tags = look_for_new_tags(cached_tags)
    for device in cached_devices:
        tags = get_all_device_tags(device)
        for key in tags.keys():
            print(tags[key])
