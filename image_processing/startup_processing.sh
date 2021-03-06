#!/bin/bash

#echo "Waiting 1s for things to startup"
#sleep 1

#echo "Setting pixel format"
#export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libv4l/v4l2convert.so
#sleep 1

#echo "Making sure nothing is using the cameras"
#fuser -k /dev/video0
#sleep 1
#fuser -k /dev/video1
#sleep 1

#echo "Changing camera settings"
# Below is for the Logitech C270
#/usr/bin/v4l2-ctl -d /dev/video0 --set-fmt-video=width=640,height=480,pixelformat=1
#sleep 1
#/usr/bin/v4l2-ctl -d /dev/video0 -c exposure_auto=1 -c exposure_absolute=10 -c brightness=100 -c contrast=32
#sleep 1
#/usr/bin/v4l2-ctl -d /dev/video1 --set-fmt-video=width=640,height=480,pixelformat=1
#sleep 1
#/usr/bin/v4l2-ctl -d /dev/video1 -c exposure_auto=1 -c exposure_absolute=10 -c brightness=100 -c contrast=32
#sleep 1

echo "Launching image processing script"
/usr/bin/python2.7 /home/ubuntu/Documents/FIRST_Image_Processing/image_processing/flush_camera.py

echo "Launching image processing script"
/usr/bin/python2.7 /home/ubuntu/Documents/FIRST_Image_Processing/image_processing/image_processing_2017frc.py

exit 0
