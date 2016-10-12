import time
from networktables import NetworkTable
import logging
logging.basicConfig(level=logging.DEBUG)


ip = '192.168.0.101'

NetworkTable.setIPAddress(ip)
NetworkTable.setClientMode()
NetworkTable.initialize()

sd = NetworkTable.getTable("Camera")

i = 0
while True:
    try:
        print 'Xval:' + str(sd.getNumber('Xval'))
    except KeyError:
        print 'robotTime: N/A'

    time.sleep(1)