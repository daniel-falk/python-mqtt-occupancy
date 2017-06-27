import paho.mqtt.client as mqtt
import socket
from time import sleep
from random import randint

from occacc.log import logger


class Mqtt(object):
    connected = 0
    topics = []

    def __init__(self, server='127.0.0.1', username=None, password=None, client_id=str(randint(1e10,9e10)), keepalive=60, min_retry_time=2, max_retry_time=60):
        self.SERVER = server
        self.KEEP_ALIVE = keepalive
        self.MIN_RETRY_TIME = min_retry_time
        self.MAX_RETRY_TIME = max_retry_time
        self.retry_time = min_retry_time
        self.client_id = client_id

        self.client = mqtt.Client(client_id=client_id, clean_session=True, userdata=self)
        if not username is None and not password is None:
            self.client.username_pw_set(username, password=password)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect


    '''
    try to connect to mqtt server
    '''
    def try_connect(self):
        while(not self.connected):
            try:
                self.client.connect(self.SERVER, keepalive=self.KEEP_ALIVE)
                self.connected = True
            except socket.error:
                logger("Failed to connect to mqtt... Retrying in {} seconds".format(self.retry_time))
                sleep(self.retry_time)
                self.retry_time = min(self.MAX_RETRY_TIME, self.retry_time*2)


    '''
    start listening on mqtt
    '''
    def start(self, topics):
        if isinstance(topics, str):
            topics = [topics]
        self.topics = topics
        self.try_connect()

        self.client.loop_start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.client.loop_stop()


'''
callback for paho on mqtt connected
'''
def on_connect(client, mqtt, rc):
    if rc == 0:
        logger("Connected to mqtt")
        for topic in mqtt.topics:
            logger("Subscribing to topic: {}".format(topic))
            client.subscribe(topic, 1)
        return
    logger("Connection to mqtt failed with status " + str(rc))
    mqtt.connected = False
    sleep(mqtt.retry_time)
    mqtt.retry_time = min(mqtt.MAX_RETRY_TIME, mqtt.retry_time*2)
    mqtt.try_connect()


'''
callback for paho on mqtt disconnect
'''
def on_disconnect(client, mqtt, rc):
    logger("Disconnected from mqtt with reason {}...".format(rc))
    mqtt.connected = False
    if rc != 0:
        mqtt.try_connect()
