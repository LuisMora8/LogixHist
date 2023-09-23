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

    def stop_thread_and_remove_device(self, device: Device):
        thread = device_threads.pop(device, None)
        if thread:
            thread.exit_event.set()
            thread.join()
            cached_devices.remove(device)

    def add_device_and_start_thread(self, device: Device):
        thread = DeviceThread(device)
        device_threads[device] = thread
        cached_devices.append(device)
        cached_tags[device] = []
        thread.start()

    def update_device_cache(self, operation: str, device: Device):
        if operation == 'delete' and device in cached_devices:
            self.stop_thread_and_remove_device(device)

        elif operation == 'add' and device not in cached_devices:
            self.add_device_and_start_thread(device)

    def update_tags_cache(self, operation: str, tag: Tag, device: Device):
        if operation == 'delete' and device in cached_tags and tag in cached_tags[device]:
            # Pause the thread reading the tag
            device_threads[device].pause_event.set()

            if self.delete_tag_points_from_db(tag):
                cached_points.pop(tag)
                cached_tags[device].remove(tag)

            else:
                print(f"Failed to delete tag: {tag.device_tag_name}")

            device_threads[device].pause_event.clear()  # Resume thread

        elif operation == 'add' and device in cached_tags and tag not in cached_tags[device]:
            cached_tags[device].append(tag)

    # User needs to delete tag from database, delete all points first
    def delete_tag_points_from_db(self, tag: Tag):
        if tag.data_type == 'int':
            all_tag_points = IntegerPoint.query.filter_by(tag_id=tag.id)
        elif tag.data_type == 'float':
            all_tag_points = FloatPoint.query.filter_by(tag_id=tag.id)
        elif tag.data_type == 'string':
            all_tag_points = StringPoint.query.filter_by(tag_id=tag.id)
        elif tag.data_type == 'bool':
            all_tag_points = BoolPoint.query.filter_by(tag_id=tag.id)
        else:
            print("Failed to query all points")
            return False
        all_tag_points.delete()
        tag_query = Tag.query.filter_by(id=tag.id)
        tag_query.delete()
        db.session.commit()
        return True

    def callback(self, ch, method, properties, body):

        # Deserialize the JSON message body and process message:
        data = json.loads(body)
        with app.app_context():

            try:
                if data['object'] == 'device':
                    # Query the device of interest by name
                    device = Device.query.filter_by(
                        device_name=data['name']).first()

                    if device:
                        self.update_device_cache(
                            operation=data['operation'], device=device)

                elif data['object'] == 'tag':
                    # Query the tag of interest by name
                    tag = Tag.query.filter_by(tag_name=data['name']).first()

                    if tag:
                        device = tag.device
                        self.update_tags_cache(
                            operation=data['operation'], tag=tag, device=device)

                        # Task was processed, acknowlede
                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                print(e)

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
        self.pause_event = threading.Event()
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

                    tags = cached_tags[self.device]

                    for tag in tags:

                        # Thread paused by MessageThread, will restart loop to get updated tags list
                        if self.pause_event.is_set():
                            self.pause_event.wait()
                            break

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
