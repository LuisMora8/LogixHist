import pika
import json


def send_message_to_rabbitmq(message: dict) -> bool:
    try:
        # Connect to message broker
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='db_update')
        # Serialize the dictionary to json string
        message_body = json.dumps(message)

        # Send message to default exchange
        channel.basic_publish(
            exchange='', routing_key='db_update', body=message_body)
        print("Sent 'Message!'")
        # Flush network buffers, close connection
        connection.close()

    except Exception as error:
        print(f"An exception occured sending to RabbitMQ: {error}")
        return False
    else:
        return True


def create_tag():

    message = {
        "object": "tag",
        "operation": "add",
        "tag_name": "string2",
    }

    send_message_to_rabbitmq(message=message)


create_tag()
