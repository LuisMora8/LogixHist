import pika

def send_message_to_rabbitmq(message: str) -> bool:
  try:
    # Connect to message broker
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='db_update')
    # Send message to default exchange
    channel.basic_publish(exchange='', routing_key='db_update', body=message)
    print("Sent 'Message!'")
    # Flush network buffers, close connection
    connection.close()
  
  except Exception as error:
    print(f"An exception occured sending to RabbitMQ: {error}")
    return False
  else:
    return True