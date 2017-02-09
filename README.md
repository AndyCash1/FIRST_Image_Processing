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

Then, open a terminal in the location where that was downloaded to.
Run the following commands:

chmod +x JetPack-${VERSION}.run
./JetPack-${VERSION}.run

Now walk through all the prompts, making sure to select TK1 and not TX1.

You'll need to connect the jetson to the same network as the laptop via an ethernet cable.
You also need to connect the jetson to the laptop via the included mini USB to USB cable.

### Install opencv on jetson

Run the following commands from a terminal:

1. sudo apt-get install build-essential
2. sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
3. sudo apt-get install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

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

sudo apt-get install v4l-utils

To display connected webcams, run the following command:

v4l2-ctl --list-devices

### Install pynetworktables

Run the following command:

sudo pip install pynetworktables

### Install pandas

Run the following command:

sudo apt-get install python-pandas

### Clone this repo on jetson

First, install git using the following commands:

sudo apt-get update

sudo apt-get install git

Then, set up your username and email:

git config --global user.name "Your Name"

git config --global user.email "youremail@domain.com"

Now, clone this repo in a directory you want it:

git clone https://github.com/AndyCash1/FIRST_Image_Processing

### Determine Webcam settings

sudo apt-get install uvcdynctrl

uvcdynctrl -c -v

## Running the image detection code on the Jetson manually

Navigate to the image_processing folder from the repo just cloned.
Run startup_processing.sh

## Running the image detection code on Jetson start up

First, disable requiring password on startup:

1. navigate to user accounts

2. click unlock, type password

3. Toggle automatic login to on

Next, place the included rc.local file located in image_processing into 
the /etc/ directory with the following command, from the image_processing directory:

sudo cp rc.local /etc

Now, give that file the correct permissions, running the following commands:

1. sudo chown root /etc/rc.local
2. sudo chmod 755 /etc/rc.local

Permissions can be checked by running:

ls -l /etc/rc.local

Now, the image processing will startup at boot!

You can kill the process by running the following command:

ps -ef | grep python

Find the PID of the process (left most number) and then run:

sudo kill <PID>

## Connecting to the RoboRio

### RoboRio Config

First connect the rio to the laptop via USB cable.

roborio IP address should be 10.13.29.2 (for Team 1329 config).

To modify the rio's settings, connect it to a PC via USB and type 172.22.11.2 
into a Firefox browser.  You will need to install MS Silverlight (Chrome does not support).
The network configuration option is where you can modify the IP of the rio.

In this configuration, the Jetson will talk to the RoboRio directly, 
and then the rio will put its values on the driverstation smart dashboard to visualize.
The ethernet cable needs to go from the jetson to the rio.

### Jetson config

Thus, the jetson needs to be on the same network as the Rio.  I have it set up as follows
IP: 10.13.29.11
Netmask: 255.0.0.0
Gateway: 0.0.0.0

In the python code, use the following: 

NetworkTable.SetIPAddress('10.13.29.2')

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

## Algorithm discussion

Todo...
