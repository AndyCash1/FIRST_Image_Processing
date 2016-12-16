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

Download opencv 2.4.9 from here:

http://opencv.org/downloads.html

navigate to where the zip file was downloaded.  Run the following commands:

unzip opencv-2.4.9.zip
cd opencv-2.4.9.zip
mkdir build
cd build
cmake -D WITH_CUDA=OFF ..
make
sudo make install

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

Run the following command:

sudo pip install pynetworktables

### Install pandas

Run the following command:

sudo apt-get install python-pandas

## Running the image detection code on the Jetson

This is assuming you are using a Microsoft Lifecam HD 3000.  Other cameras will have slightly different settings.

Run the following command in a terminal:

v4l2-ctl -d /dev/video0 -c exposure_auto=1 -c exposure_absolute=$1 -c brightness=30 -c contrast=10

Then run the python script:

python detect_u_shapes_linux.py

## Algorithm discussion

Todo...

## Connecting to the RoboRio

### RoboRio Config

First connect the rio to the laptop via USB cable.

roborio IP address should be 10.13.27.22 (for Team 1327 config).

To modify the rio's settings, connect it to a PC via USB and type 172.22.11.2 
into a Firefox browser.  You will need to install MS Silverlight (Chrome does not support).
The network configuration option is where you can modify the IP of the rio.

In this configuration, the Jetson will talk to the RoboRio directly, 
and then the rio will put its values on the driverstation smart dashboard to visualize.
The ethernet cable needs to go from the jetson to the rio.

### Jetson config

Thus, the jetson needs to be on the same network as the Rio.  I have it set up as follows
IP: 10.13.27.100
Netmask: 255.0.0.0
Gateway: 0.0.0.04

In the python code, use the following: 

NetworkTable.SetIPAddress('10.13.27.22')

Which will make the jetson put its values on the RoboRio's networktable.
Follow the driver station example at this link:

http://pynetworktables.readthedocs.io/en/stable/examples.html#robot-example

## Running the algorithm

Open up a cmd terminal on the jetson.  Ensure the lifecam 3000 is properly detected by running 
the following command:

v4l2-ctl --list-devices

Then, run the following command to modify the exposure settings:

v4l2-ctl -d /dev/video0 -c exposure_auto=1 -c exposure_absolute=$1 
-c brightness=30 -c contrast=10

The image will pop up and when the object is detected, it will be highlighted with a red outline.
Also, the terminal will show the features extracted.

Back on the driverstation, those features should now be visible on the smartdashboard, 
after you put teleop mode on.
