import sys
import os
import errno
from datetime import datetime
from enum import Enum
from threading import current_thread
import re

from occacc.config import ERROR_DIR

# Error message to pass in the IPC queue
class ErrorMessage(object):
    def __init__(self, src, short, long):
        self.src = src
        self.short = short
        self.long = long


class ErrorFilter(object):

    def __init__(self, queue):
        self.q = queue

    def write(self, string):
        if 'Exception' in string or 'Traceback' in string:
            err = ErrorMessage(
                    current_thread().name,
                    'Exception' if 'Exception' in string else 'Error Traceback',
                    string)
            logger(err, log_level=LOG.FATAL)
            self.q.put(err)
        else:
            logger(string, LOG.ERROR)


class LOG(Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    FATAL = 'FATAL'


def write_to_file(message):
    # Create path if not exists
    if not os.path.exists(ERROR_DIR):
        try:
            os.makedirs(ERROR_DIR)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    # Find a free filename
    fpath = '{}/exception_{}.log'
    i = 1
    while os.path.exists(fpath.format(ERROR_DIR, i)):
        i+=1
    fpath = fpath.format(ERROR_DIR, i)
    # Write file
    with open(fpath, 'w') as f:
        f.write(message)
    return fpath


def logger(message, log_level=LOG.INFO):

    def put(level, message):
        prefix = "{time} [{level}]: ".format(time=datetime.now(), level=level)
        message = message.replace('\n', '\n{}'.format(' '*len(prefix)))
        print(prefix + message)

    if isinstance(message, ErrorMessage):
        fpath = write_to_file(message.long)
        reason = message.long[message.long.rfind('\n ')+1:-1:]\
                .strip()\
                .replace('\n', ' / ')
        message = "{} triggered {} : {}\nFull exception saved in file: {}".format(
                message.src, message.short, reason, fpath)
    elif not isinstance(message, str):
        message = "Unknown message type:\n{}".format(str(message))

    if re.search('^[\n\s]*$', message):
        return

    if not isinstance(log_level, LOG):
        put(LOG.ERROR.value, 'Logging with unknown log-level:')
        put('?', message)

    put(log_level.value, message)

    sys.stdout.flush() # Flush to systemd journal to prevent long delays..

