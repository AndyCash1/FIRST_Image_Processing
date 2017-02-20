import os
import cv2

print "Default"
os.system('v4l2-ctl -d /dev/video0 -V')

print "After setting MJPG, before opencv"
os.system('/usr/bin/v4l2-ctl -d /dev/video0 --set-fmt-video=width=640,height=480,pixelformat=1')
os.system('v4l2-ctl -d /dev/video0 -V')

cap = cv2.VideoCapture(0)
im = cap.read()

print "After opencv"
os.system('v4l2-ctl -d /dev/video0 -V')