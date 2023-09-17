import pika
import sys
import os


if __name__ == '__main__':
    try:
        # receive_messages()
        print('hi')
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
