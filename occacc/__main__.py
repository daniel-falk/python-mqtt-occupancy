import sys
from signal import signal, SIGINT
from threading import Thread
try:
    from Queue import Queue # Python2
except ImportError:
    from queue import Queue # Python3

from occacc.logger import logger, LOG, ErrorFilter, ErrorMessage
from occacc.mqtt import Mqtt
from occacc.config import MQTT, CAMERAS, COMMAND_PREFIX
from occacc.occupancy import on_passage, on_correction


def handler(signal, frame):
    sys.exit(0)


def start_process():
    # Config up MQTT
    mqtt = Mqtt(**MQTT)
    # Topics  for passages
    topics = list(CAMERAS)
    mqtt.client.on_message = on_passage
    # Topics for correction commands, only for masters/zones
    for ztopic in list(value['zone_topic'] for key, value in CAMERAS.items() if 'zone_topic' in value):
        topic = '{}/{}'.format(COMMAND_PREFIX,ztopic)
        topics.append(topic)
        mqtt.client.message_callback_add(topic, on_correction)
    for t in topics:
        mqtt.client.subscribe(t, 1)

    th = Thread(target=mqtt.start, args=(topics,))
    th.daemon = True
    th.start()
    return th


if __name__ == "__main__":

    signal(SIGINT, handler)

    # Create a thread safe queue object from IPC
    queue = Queue()

    # Redirect stderr to a filter object
    # We use this to search for exception in other worker threads and exit module
    # to trigger systemd to restart module.
    sys.stderr = ErrorFilter(queue)

    start_process()

    while True:
        msg = queue.get()
        if isinstance(msg, ErrorMessage):
            logger('Exception in thread detected, exiting...', LOG.FATAL)
            break
