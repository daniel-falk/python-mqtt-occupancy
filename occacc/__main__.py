from occacc import mqtt_conf, cameras
from occacc.db_models import db, Occupancy
from occacc.mqtt import Mqtt
from occacc.log import logger

from requests import get
from requests.auth import HTTPDigestAuth as digest

# TODO: Move to a config file...
OCCUPANCY_TOPIC = 'home/occupancy'
OCCUPANCY_CORRECTION_TOPIC = 'commands/home/occupancy'

# Read camera ip's from the status topics using mqtt and parse from matching topic names?
# Store passwords in a network global vault?
OCCUPANCY_MASTERS =  {
    '192.168.0.99' : {
        'username' : 'root',
        'password' : '****'
    }
}

'''
On a passage the occupancy should be incremented in the database
and the new value should be published
'''
def on_passage(client, userdata, message):
    print(message.topic)
    # Get last count
    last_occ = db.query(Occupancy).order_by(Occupancy.time.desc()).first()
    count = 0 if last_occ is None else last_occ.occ

    # Change according to direction
    diff = None
    payload = message.payload.decode('utf-8')
    if payload == 'in':
        diff = 1
    elif payload == 'out':
        diff = -1
    else:
        logger('WARNING: Unknown direction "{}" at topic "{}"'.format(message.payload, message.topic))

    # Get camera location name
    try:
        location = cameras[message.topic]
    except KeyError:
        location = 'unknown: {}'.format(message.topic)

    if not diff is None:
        count += diff
        # Update database
        occ = Occupancy(occ=count, diff=diff, location=location)
        db.add(occ)
        db.commit()
        # Send mqtt update
        client.publish(OCCUPANCY_TOPIC, payload=count, qos=1, retain=1)


'''
When a correction of the occupancy is received the values should be
updated in the database and the new value published
'''
def on_correction(client, userdata, message):
    try:
        count = int(message.payload)
    except ValueError:
        print('Unknown correction value: {}'.format(message.payload))
        return # TODO: Implement a estimation confidence, like: '<new_value>, <confidence>'
    # Update database
    occ = Occupancy(occ=count, diff=0, location='correction')
    db.add(occ)
    db.commit()
    # Set the new occupancy in the AXIS Occupancy Estimators
    for ip in OCCUPANCY_MASTERS:
        r = get('http://{}/local/occupancy-estimator/.apioperator?occupancy-reset&occ={}'.format(ip, count),
                auth=digest(*OCCUPANCY_MASTERS[ip].values())) # Order might get messed up depending on python version... But probably not ;)
        r.raise_for_status()
        r = r.json()
        if r['status'] != 'OK':
            raise RuntimeError('Failed to set camera occupancy')
    # Publish mqtt update
    client.publish(OCCUPANCY_TOPIC, payload=count, qos=1, retain=1)



mqtt = Mqtt(**mqtt_conf)
topics = list(cameras)
topics.append(OCCUPANCY_CORRECTION_TOPIC)
mqtt.client.on_message = on_passage
mqtt.client.message_callback_add(OCCUPANCY_CORRECTION_TOPIC, on_correction)
for t in topics:
    mqtt.client.subscribe(t, 1)
mqtt.start(topics)
