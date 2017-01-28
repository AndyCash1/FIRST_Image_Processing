#!/bin/bash

echo "Waiting 10s for things to startup"
sleep 10

echo "Setting pixel format"
export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libv4l/v4l2convert.so
sleep 2

echo "Changing camera settings"
/usr/bin/v4l2-ctl -d /dev/video0 -c exposure_auto=1 -c exposure_absolute=$1 -c brightness=30 -c contrast=10
sleep 2

echo "Making sure nothing is using the camera"
fuser -k /dev/video0
sleep 5

echo "Launching image processing script"
/usr/bin/python2.7 /home/ubuntu/Documents/image_processing/image_processing_2017frc.py

exit 0

