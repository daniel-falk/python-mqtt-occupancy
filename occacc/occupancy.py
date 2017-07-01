from occacc.config import CAMERAS, COMMAND_PREFIX
from occacc.logger import logger, LOG
from occacc.db_models import db, Occupancy

from requests import get
from requests.auth import HTTPDigestAuth as digest
from requests import codes

'''
On a passage the occupancy should be incremented in the database
and the new value should be published
'''
def on_passage(client, userdata, message):
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
        logger('Unknown direction "{}" at topic "{}"'.format(message.payload, message.topic), LOG.ERROR)

    # Get camera location name
    try:
        camera = CAMERAS[message.topic]
        location = camera['location']
    except KeyError:
        logger('unknown topic: {}'.format(message.topic), LOG.ERROR)
        return

    if not diff is None:
        count += diff
        # Update database
        occ = Occupancy(occ=count, diff=diff, location=location)
        db.add(occ)
        db.commit()
        # Send mqtt update
        client.publish(camera['zone_topic'], payload=count, qos=1, retain=1)


'''
When a correction of the occupancy is received the values should be
updated in the database and the new value published
'''
def on_correction(client, userdata, message):
    try:
        count = int(message.payload)
    except ValueError:
        logger('Unknown correction value: {}'.format(message.payload), LOG.ERROR)
        return # TODO: Implement a estimation confidence, like: '<new_value>, <confidence>'
    # Update database
    occ = Occupancy(occ=count, diff=0, location='correction')
    db.add(occ)
    db.commit()
    # Set the new occupancy in the AXIS Occupancy Estimators
    update_camera_occupancy(CAMERAS, count)
    # Publish mqtt update
    if message.topic.startswith("{}/".format(COMMAND_PREFIX)):
        client.publish(
                message.topic[len("{}/".format(COMMAND_PREFIX))::],
                payload=count, qos=1, retain=1)
    else:
        logger("Unknown correction topic: {}".format(message.topic), LOG.ERROR)


def update_camera_occupancy(cameras, count):
    for topic, camera in dict((key, value) for key, value in cameras.items() if 'is_master' in value).items():
        r = get('http://{}/local/occupancy-estimator/.api?occupancy-reset&occ={}'.format(camera['ip'], count),
                auth=digest(camera['username'], camera['password']))
        if r.status_code != codes.ok:
            logger("Failed to set camera occupancy, status code was {}".format(r.status_code), LOG.ERROR)
        else:
            r = r.json()
            if r['status'] != 'OK':
                logger('Failed to set camera occupancy, status was %s' % r['status'], LOG.ERROR)

