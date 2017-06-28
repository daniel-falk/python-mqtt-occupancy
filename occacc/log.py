import sys

def logger(message, error=0):
    if (error):
        print("ERROR: {}".format(message))
    else:
        print(message)
    sys.stdout.flush() # Flush to systemd journal to prevent long delays..

