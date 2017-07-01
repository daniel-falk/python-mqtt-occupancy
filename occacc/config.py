# Folder to put exception log files in
ERROR_DIR = '/mnt/externhdd/log/occupancy'

# Prefix for the topic if its a command
COMMAND_PREFIX = 'commands'

# Camera IP, location and occupancy master status should be implemented as
# retained status topics in the Axis camera..
# Password and username could be saved in a network-global vault
CAMERAS =  {
    'camera/ACCC8E7E8F61/AXIS_Occupancy_Estimator/0/passage' : {
        'ip' : '192.168.0.99',
        'username' : 'root',
        'password' : '****',
        'location' : 'Hallway',
        'is_master' : True,
        'zone_topic' : 'home/occupancy'
    }
}


# Sql database info
SQL = dict(
        type = 'mysql',
        host = '192.168.0.80',
        username = 'IoT_nodes',
        password = '*********',
        database = 'IoT')


# MQTT connection details
MQTT = dict(
        server = '192.168.0.80')
