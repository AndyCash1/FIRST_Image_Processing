# FIRST_Image_Processing
This repo contains code for image processing for the FIRST FRC competition. 

## Nvidia Jetson co-processor set up

This section details how to set up a Jetson TK1.  

### Initial Jetson Flash

You will need an Ubuntu 14.04 PC... either set up 
dual boot or boot from a flash drive with the image.  The ubuntu image can be found at the following link

http://releases.ubuntu.com/14.04/

Once that is set up, download jetpack from the following link:

https://developer.nvidia.com/embedded/jetpack

You'll need to connect the jetson to the same network as the laptop via an ethernet cable.  
You also need to connect the jetson to the laptop via the included mini USB to USB cable.

### Install opencv

### Install pip

Run the following 3 commands in sequence:

sudo apt-get install python-pip python-dev build-essential
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv

### Install v4l

Run the following command:

sudo apt-get v4l-utils

To display connected webcams, run the following command:

v4l2-ctl --list-devices

### Install pynetworktables

### Install pandas

Run the following command:

sudo apt-get install python-pandas

## Running the image detection code on the Jetson

This is assuming you are using a Microsoft Lifecam HD 3000.  Other cameras will have slightly different settings.

Run the following command in a terminal:

v4l2-ctl -d /dev/video0 -c exposure_auto=1 -c exposure_absolute=$1 -c brightness=30 -c contrast=10

Then run the python script:

python detect_u_shapes_linux.py




