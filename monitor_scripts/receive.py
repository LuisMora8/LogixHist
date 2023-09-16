import pika
import sys
import os


def callback(ch, method, properties, body):
    print(f" [x] Received {body}")
    # task was processed, acknowlede
    ch.basic_ack(delivery_tag=method.delivery_tag)


def receive_messages():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='db_update')
    channel.basic_consume(queue='db_update', on_message_callback=callback)

    channel.start_consuming()


if __name__ == '__main__':
    try:
        receive_messages()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
