import os
import cv2
import time

NUM_FRAMES = 20

def flush_camera():
    print "flushing camera..."
    
    os.system('/usr/bin/v4l2-ctl -d /dev/video0 --set-fmt-video=width=640,height=480,pixelformat=1')
    time.sleep(1)
    os.system('/usr/bin/v4l2-ctl -d /dev/video1 --set-fmt-video=width=640,height=480,pixelformat=1')
    time.sleep(1)
    
    os.system('/usr/bin/v4l2-ctl -d /dev/video0 -c exposure_auto=1')
    os.system('/usr/bin/v4l2-ctl -d /dev/video0 -c exposure_absolute=7')
    os.system('/usr/bin/v4l2-ctl -d /dev/video0 -c brightness=100')
    os.system('/usr/bin/v4l2-ctl -d /dev/video0 -c contrast=32')
    os.system('/usr/bin/v4l2-ctl -d /dev/video0 -c gain=64')
    os.system('/usr/bin/v4l2-ctl -d /dev/video0 -c white_balance_temperature_auto=0')
    os.system('/usr/bin/v4l2-ctl -d /dev/video0 -c white_balance_temperature=4000')
    
    time.sleep(1)
    os.system('/usr/bin/v4l2-ctl -d /dev/video1 -c exposure_auto=1')
    os.system('/usr/bin/v4l2-ctl -d /dev/video1 -c exposure_absolute=7')
    os.system('/usr/bin/v4l2-ctl -d /dev/video1 -c brightness=100')
    os.system('/usr/bin/v4l2-ctl -d /dev/video1 -c contrast=32')
    os.system('/usr/bin/v4l2-ctl -d /dev/video1 -c gain=64')
    os.system('/usr/bin/v4l2-ctl -d /dev/video1 -c white_balance_temperature_auto=0')
    os.system('/usr/bin/v4l2-ctl -d /dev/video1 -c white_balance_temperature=4000')
    time.sleep(1)
    
    camera0 = cv2.VideoCapture(0)
    camera1 = cv2.VideoCapture(1)
    
    for i in range(0, NUM_FRAMES):
        img = camera0.read()[1]
        img = camera1.read()[1]
        print i
    
    print "camera flush complete"
    
if __name__ == "__main__":
    flush_camera()