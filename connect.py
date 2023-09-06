from pylogix import PLC


def monitor_tags():

    with PLC("192.168.1.231") as comm:
        while True:
            result = comm.Read("test_string")
            print(result)
