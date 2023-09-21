from pylogix import PLC, lgx_response
from flask import Flask
from db_models import db, Device, Tag, IntegerPoint, FloatPoint, StringPoint, BoolPoint
from sqlalchemy import desc

import threading
import pika
import json


# Remote Debugging
import ptvsd
ptvsd.enable_attach(address=('0.0.0.0', 5678))
ptvsd.wait_for_attach()


app = Flask(__name__)
database_uri = 'mysql://luis:developer@mysql:3306/logixhistorian'
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db.init_app(app)

device_threads = {}
cached_devices = []
cached_tags = {}
cached_points = {}

# cached_devices
# [device, device]


# cached_tags
# {
#     device:
#         [
#             tag,
#         ],
# }


# cached_points
# {
#     <tag_id>: last_point.value,
# }


''' Initialization - Read From Database and Initialize Cache '''


def initialize_cache():
    with app.app_context():

        db_devices = Device.query.all()  # Query and store devices into cached_devices
        for d in db_devices:
            cached_devices.append(d)

        for device in cached_devices:
            tags_associated_with_device = Tag.query.filter_by(
                device_id=device.id)  # Query device tags and store tags into cached_tags

            cached_tags[device] = []
            for t in tags_associated_with_device:
                cached_tags[device].append(t)

            # Query the most recent point of the given tag
            for tag in cached_tags[device]:
                if tag.data_type == 'int':
                    point = IntegerPoint.query.filter_by(tag_id=tag.id).order_by(
                        desc(IntegerPoint.timestamp)).first()
                elif tag.data_type == 'float':
                    point = FloatPoint.query.filter_by(tag_id=tag.id).order_by(
                        desc(FloatPoint.timestamp)).first()
                elif tag.data_type == 'string':
                    point = StringPoint.query.filter_by(tag_id=tag.id).order_by(
                        desc(StringPoint.timestamp)).first()
                elif tag.data_type == 'bool':
                    point = BoolPoint.query.filter_by(tag_id=tag.id).order_by(
                        desc(BoolPoint.timestamp)).first()
                else:
                    print(
                        f"Failed to Read Data Point from Database: {tag.tag_name}")

                if point:
                    cached_points[tag] = point.value
                else:  # New tag no points yet in database
                    cached_points[tag] = None

    print("Succesfully updated cache")


''' Message Broker Communication '''


class MessageThread(threading.Thread):
    def __init__(self, queue: str):
        super().__init__()
        self.queue = queue
        self.exit_event = threading.Event()

    def stop_thread_and_remove_device(device: Device):
        thread = device_threads.pop(device, None)
        if thread:
            thread.exit_event.set()
            thread.join()
            cached_devices.remove(device)

    def update_device_cache(self, operation: str, device: Device):
        if operation == 'delete':
            self.stop_thread_and_remove_device(device)
        elif operation == 'add':
            cached_devices.append(device)

    def update_tags_cache(self, operation: str, tag: Tag, device: Device):
        if operation == 'delete':
            cached_tags[device].remove(tag)
        elif operation == 'add':
            cached_tags[device].append(tag)

    def callback(self, ch, method, properties, body):

        # Deserialize the JSON message body and process message:
        data = json.loads(body)
        with app.app_context():
            breakpoint()
            if data['object'] == 'device':
                # Query the device of interest by name
                device = Device.query.filter_by(
                    device_name=data['device_name']).first()

                if device and device not in cached_devices:
                    self.update_device_cache(
                        operation=data['operation'], device=device)

            elif data['object'] == 'tag':
                # Query the tag of interest by name
                tag = Tag.query.filter_by(tag_name=data['tag_name']).first()

                if tag and tag not in cached_tags:
                    device = tag.device
                    self.update_tags_cache(
                        operation=data['operation'], tag=tag, device=device)

        # Task was processed, acknowlede
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def receive_messages(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='logix-historian-rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_consume(
            queue=self.queue, on_message_callback=self.callback)

        channel.start_consuming()

    def run(self):
        self.receive_messages()


''' Monitor Tags for the Device '''


class DeviceThread(threading.Thread):
    def __init__(self, device: Device):
        super().__init__()
        self.device = device
        self.exit_event = threading.Event()

    def create_point_in_db(self, tag: Tag, response: lgx_response.Response):
        if tag.data_type == 'int':
            point = IntegerPoint(tag, response.Value)
        elif tag.data_type == 'float':
            point = FloatPoint(tag, response.Value)
        elif tag.data_type == 'string':
            point = StringPoint(tag, response.Value)
        elif tag.data_type == 'bool':
            point = BoolPoint(tag, response.Value)
        else:
            print("Failed to Create Data Point in Database: Incorrect Data Type")
            return

        db.session.add(point)
        db.session.commit()
        cached_points[tag] = response.Value  # update cache
        print("Successfully updated tag in database")

    def monitor_tags(self):
        with PLC(self.device.ip_address) as comm:
            while not self.exit_event.is_set():

                try:

                    tags = cached_tags[device]

                    for tag in tags:

                        # Read the tag from PLC
                        response = comm.Read(tag=tag.device_tag_name)
                        if response.Status != 'Success':  # Could not connect to PLC
                            continue

                        # Compare to cache, if exists
                        if tag in cached_points:
                            last_value = cached_points[tag]
                        else:
                            last_value = None

                        if last_value is None or response.Value != last_value:  # Different value or new tag
                            with app.app_context():
                                self.create_point_in_db(
                                    tag=tag, response=response)

                except Exception as e:
                    print(f"Exception in monitor_tags: {e}")

    def run(self):
        self.monitor_tags()


# Driver Code
if __name__ == '__main__':
    initialize_cache()

    receive_message_thread = MessageThread(queue='db_update')
    receive_message_thread.start()

    for device in cached_devices:
        thread = DeviceThread(device)
        device_threads[device] = thread
        thread.start()
