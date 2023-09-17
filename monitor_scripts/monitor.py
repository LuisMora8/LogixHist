from pylogix import PLC
from flask import Flask
from db_models import db, Device, Tag, IntegerPoint, FloatPoint, StringPoint, BoolPoint
from query_functions import tag_value_query

import threading
import pika
import json

app = Flask(__name__)
# MacOS MySQL
# database_uri = 'mysql://luis:developer@localhost/logixhistorian'
database_uri = 'mysql://luis:developer@mysql:3306/logixhistorian'
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db.init_app(app)


cached_devices = []
cached_tags = {}
# {
#     device:
#         [
#             tag,
#         ],
# }
cached_points = {}
# {
#     <tag_id>: value,
# }

''' Message Broker Communication'''


def callback(ch, method, properties, body):

    # Deserialize the JSON message body and process message:
    data = json.loads(body)

    global cached_devices
    global cached_tags

    if data['object'] == 'device':
        # Query the device of interest by name
        device = Device.query.filter_by(
            device_name=data['device_name']).first()

        cached_devices = update_device_cache(
            cached_devices=cached_devices, operation=data['operation'], device=device)  # Update the cache

    elif data['object'] == 'tag':
        # Query the tag of interest by name
        tag = Tag.query.filter_by(tag_name=data['tag_name']).first()
        device = tag.device
        tags = cached_tags[device]

        cached_tags[device] = update_tags_cache(
            tags, data['operation'], tag=tag)

    # Task was processed, acknowlede
    ch.basic_ack(delivery_tag=method.delivery_tag)


def receive_messages():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='db_update')
    channel.basic_consume(queue='db_update', on_message_callback=callback)

    channel.start_consuming()


def update_device_cache(cached_devices: [Device], operation: str, device: Device):
    if operation == 'delete':
        cached_devices.remove(device)
    elif operation == 'add':
        cached_devices.append(device)

    return cached_devices


def update_tags_cache(cached_tags: [Tag], operation: str, tag: Tag):
    if operation == 'delete':
        cached_tags.remove(tag)
    elif operation == 'add':
        cached_tags.append(tag)

    return cached_tags


''' Monitor Tags for the Device'''


def monitor_tags(device: Device, tags: [Tag]):

    with PLC(device.ip_address) as comm:

        global cached_devices
        while device in cached_devices:

            for tag in tags:

                # Read the tag and query the last point
                response = comm.Read(tag.device_tag_name)
                last_point = tag_value_query(tag=tag)

                # Compare PLC value to database value, if different then create a new point
                if last_point is None or response.Value is not last_point.value:
                    if Tag.data_type == 'int':
                        point = IntegerPoint(tag, response.Value)
                    elif Tag.data_type == 'float':
                        point = FloatPoint(tag, response.Value)
                    elif Tag.data_type == 'string':
                        point = StringPoint(tag, response.Value)
                    elif Tag.data_type == 'bool':
                        point = BoolPoint(tag, response.Value)
                    else:
                        continue

                    db.session.add(point)
                    db.session.commit()


# Driver Code
if __name__ == '__main__':
    cached_devices = look_for_new_devices(cached_devices)
    cached_tags = look_for_new_tags(cached_tags)
    for device in cached_devices:
        tags = get_all_device_tags(device)
        for key in tags.keys():
            print(tags[key])
