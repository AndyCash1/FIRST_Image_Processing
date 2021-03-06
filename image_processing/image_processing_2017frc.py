"""
This script is the main production methdod for image processing for Team 1311 Kell Robotics
It is used for the 2017 FRC competition
"""

import numpy as np
import importlib
import cv2
import copy
import time
import subprocess
import os
import random
from networktables import NetworkTable

# For purposes of outputting a debug file that lets you know the program is running
DEBUG_FILEPATH = '/home/ubuntu/Documents/FIRST_Image_Processing/image_processing/'

RIO_IP = '10.13.29.2'

# Min perimeter for the object... contours are not processed
# unless they meet both of these requirements
MIN_PERIMETER = 50
MIN_AREA = 100

# Height and width of the returned image
WIDTH = 640
HEIGHT = 480

# Approximation constant that is multiplied by perimeter
APPROX_POLYDP_FACTOR = 0.01

# Functional logicals
REALTIME_MODE = True
NETWORK_MODE = True
DISPLAY_IMAGE = True
DEBUG_TXT_FILES = False
ALLOW_SHUTDOWN = True

# Rectangle approx factors
HG_MAX_AREA_DIFF = 3
HG_MAX_PERI_DIFF = 1.5
HG_MIN_PERI_DIFF = 0.5
PEG_MAX_AREA_DIFF = 1.5
PEG_MAX_PERI_DIFF = 1.2
PEG_MIN_PERI_DIFF = 0.75

# Constants for green in H, S, V
LOWER_GREEN = np.array([60, 190, 100])
UPPER_GREEN = np.array([80, 255, 255])

# Constants for camera
HIGH_GOAL_CAM_ID = '9BCFC920'
GEAR_CAM_ID = '0F5FC920'
DEFAULT_HIGH_GOAL_CAM = 0


def determine_cameras():
    info0 = subprocess.check_output("/bin/udevadm info --query=all --name=/dev/video0", shell=True)
    info1 = subprocess.check_output("/bin/udevadm info --query=all --name=/dev/video1", shell=True)

    id0 = info0.split('ID_SERIAL_SHORT=')[1].split('\n')[0]
    id1 = info1.split('ID_SERIAL_SHORT=')[1].split('\n')[0]

    high_goal_port = -999
    gear_port = -999

    high_goal_found = -88
    gear_found = -88

    if (id0 == HIGH_GOAL_CAM_ID):
        high_goal_port = 0
    if (id0 == GEAR_CAM_ID):
        gear_port = 0
    if (id1 == HIGH_GOAL_CAM_ID):
        high_goal_port = 1
    if (id1 == GEAR_CAM_ID):
        gear_port = 1

    if (high_goal_port != -999) and (gear_port != -999):
        # Both successfully found
        high_goal_found = 44
        gear_found = 44
    elif (high_goal_port != -999) and (gear_port == -999):
        # Gear port not found, set it equal to high goal port
        high_goal_found = 44
        gear_port = high_goal_port
    elif (high_goal_port == -999) and (gear_port != -999):
        # high goal port not found, set it equal to high goal port
        gear_found = 44
        high_goal_port = gear_port
    else:
        # Neither found.  Default to 0
        high_goal_port = 0
        gear_port = 0

    return (high_goal_port, gear_port, high_goal_found, gear_found)

def calc_height_width(contour):
    """
    This method calculates The maximum distance in the X direction (width) and the
    maximum distance in the Y direction (height).  Note that this is not a true measurement,
    rather an approximation assuming the object's orientation is 0 degrees.

    it will work well if this assumption is close, but not so well if it is not.
    """

    leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
    rightmost = tuple(contour[contour[:, :, 0].argmax()][0])
    topmost = tuple(contour[contour[:, :, 1].argmin()][0])
    bottommost = tuple(contour[contour[:, :, 1].argmax()][0])

    height = bottommost[1] - topmost[1]
    width = rightmost[0] - leftmost[0]

    return (height, width)

def img_processing_main(img, hg_logical, debug_mode, debug_file):
    """
    This method is responsible for calling both of the detection algorithms (pegs and high goal)
    And then returning the results back to main
    """
    if debug_mode:
        cv2.imshow("img", img)
        cv2.waitKey(0)

    # Blur, the convert to hsv
    img_blur = cv2.GaussianBlur(img, (3, 3), 0)
    hsv_img = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)

    # Determine where the green pixels are
    mask = cv2.inRange(hsv_img, LOWER_GREEN, UPPER_GREEN)

    if debug_mode:
        cv2.imshow("mask", mask)
        cv2.waitKey(0)

    # find contours among the mask
    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if hg_logical:
        ret_val = find_highgoal(copy.deepcopy(img), cnts, debug_mode, debug_file)
    else:
        ret_val = find_gear(copy.deepcopy(img), cnts, debug_mode, debug_file)

    return ret_val

def find_gear(img, cnts, debug_mode, debug_file):
    """
    This method finds the rectangle reflective shapes that are on both sides of the
    peg, and returns features from them
    """

    # Loop thru all the contours identified in the picture
    ret_val = {}
    saved_contour = []
    for contour in cnts:

        area = cv2.contourArea(contour)
        peri = cv2.arcLength(contour, True)

        # Only consider the "larger" contours
        if peri > MIN_PERIMETER and area > MIN_AREA:

            # Validate the contour makes sense
            rect = cv2.minAreaRect(contour)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)

            rect_area = cv2.contourArea(box)
            rect_peri = cv2.arcLength(box, True)

            # The bounding rectange should be almost identical to the actual contour
            area_good = rect_area/area < PEG_MAX_AREA_DIFF
            peri_good = (rect_peri/peri < PEG_MAX_PERI_DIFF) and (rect_peri/peri > PEG_MIN_PERI_DIFF)

            if (not area_good) | (not peri_good):
                continue

            # should have larger height than width
            (height, width) = calc_height_width(contour)

            if width >= height:
                continue

            # If we are here, shape is good
            saved_contour.append(contour)
            if debug_mode:
                cv2.drawContours(img, [contour], 0, (0, 0, 255), 2)
                cv2.drawContours(img, [box], 0, (255, 255, 0), 2)

    # We have now analyzed all the contours, and are ready to see if we have the correct amount
    if len(saved_contour) == 2:

        if debug_mode:
            cv2.imshow("res", img)
            cv2.waitKey(0)

        # Extract features from the image
        M0 = cv2.moments(saved_contour[0])
        M1 = cv2.moments(saved_contour[1])

        M0_ctr_X = int(M0['m10']/M0['m00'])
        M1_ctr_X = int(M1['m10']/M1['m00'])

        if M0_ctr_X <= M1_ctr_X:
            left_obj = saved_contour[0]
            right_obj = saved_contour[1]

            left_M = M0
            right_M = M1
        else:
            left_obj = saved_contour[1]
            right_obj = saved_contour[0]

            left_M = M1
            right_M = M0

        ret_val['left_ctr_X'] = int(left_M['m10']/left_M['m00'])
        ret_val['left_ctr_Y'] = int(left_M['m01']/left_M['m00'])

        ret_val['right_ctr_X'] = int(right_M['m10']/right_M['m00'])
        ret_val['right_ctr_Y'] = int(right_M['m01']/right_M['m00'])

        ret_val['left_area'] = cv2.contourArea(left_obj)
        ret_val['right_area'] = cv2.contourArea(right_obj)

        if debug_file:
            with open(DEBUG_FILEPATH + 'logfile_peg_found.txt', 'a+') as f:
                f.write(str(ret_val['left_area']) + ', ' +
                        str(ret_val['left_ctr_X']) + ', ' +
                        str(ret_val['left_ctr_Y']) + ', ' +
                        str(ret_val['right_area']) + ', ' +
                        str(ret_val['right_ctr_X']) + ', ' +
                        str(ret_val['right_ctr_Y']) + '\n')
    else:
        # Have 1 or less contour, which means we did not detect the shape
        if debug_file:
            with open(DEBUG_FILEPATH + 'logfile_peg_notfound.txt', 'a+') as f:
                f.write(".")
        return None

    return ret_val

def find_highgoal(img, cnts, debug_mode, debug_file):
    """
    This method finds the reflective tape on the cylindrical high goal,
    and returns features from them
    """

    # Loop thru all the contours identified in the picture
    top_obj = None
    bot_obj = None
    ret_val = {}
    saved_contour = []
    for contour in cnts:

        area = cv2.contourArea(contour)
        peri = cv2.arcLength(contour, True)

        # Only consider the "larger" contours
        if peri > MIN_PERIMETER and area > MIN_AREA:

            # Validate the contour makes sense
            rect = cv2.minAreaRect(contour)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)

            rect_area = cv2.contourArea(box)
            rect_peri = cv2.arcLength(box, True)

            # Area of the bounding rectangle will always be bigger
            # than the actial object.  Make sure its not too much bigger
            area_good = rect_area/area < HG_MAX_AREA_DIFF
            peri_good = (rect_peri/peri < HG_MAX_PERI_DIFF) and (rect_peri/peri > HG_MIN_PERI_DIFF)

            if (not area_good) | (not peri_good):
                continue

            # should have larger width than height
            (height, width) = calc_height_width(contour)

            if height >= width:
                continue

            # If we are here, shape is good
            saved_contour.append(contour)
            if debug_mode:
                cv2.drawContours(img, [contour], 0, (0, 0, 255), 2)
                cv2.drawContours(img, [box], 0, (255, 255, 0), 2)

    # We have now analyzed all the contours, and are ready to see if we have the correct amount
    if len(saved_contour) == 2:

        if debug_mode:
            cv2.imshow("res", img)
            cv2.waitKey(0)

        # Extract features from the image
        area0 = cv2.contourArea(saved_contour[0])
        area1 = cv2.contourArea(saved_contour[1])

        if area0 >= area1:
            top_obj = saved_contour[0]
            bot_obj = saved_contour[1]
            ret_val['top_area'] = area0
            ret_val['bot_area'] = area1
        else:
            top_obj = saved_contour[1]
            bot_obj = saved_contour[0]
            ret_val['top_area'] = area1
            ret_val['bot_area'] = area0

        M = cv2.moments(top_obj)
        ret_val['top_ctr_X'] = int(M['m10']/M['m00'])
        ret_val['top_ctr_Y'] = int(M['m01']/M['m00'])

        M = cv2.moments(bot_obj)
        ret_val['bot_ctr_X'] = int(M['m10']/M['m00'])
        ret_val['bot_ctr_Y'] = int(M['m01']/M['m00'])

        if debug_file:
            with open(DEBUG_FILEPATH + 'logfile_highgoal_found.txt', 'a+') as f:
                f.write(str(ret_val['top_area']) + ', ' +
                        str(ret_val['top_ctr_X']) + ', ' +
                        str(ret_val['top_ctr_Y']) + ', ' +
                        str(ret_val['bot_area']) + ', ' +
                        str(ret_val['bot_ctr_X']) + ', ' +
                        str(ret_val['bot_ctr_Y']) + '\n')
    else:
        # Have 1 or less contour, which means we did not detect the shape
        if debug_file:
            with open(DEBUG_FILEPATH + 'logfile_highgoal_notfound.txt', 'a+') as f:
                f.write(".")
        return None

    return ret_val

def main():
    """
    Main method for image processing
    """

    if REALTIME_MODE:
        time.sleep(1)

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

        (high_goal_port, gear_port, high_goal_found, gear_found) = determine_cameras()

        camera_hg = cv2.VideoCapture(high_goal_port)
        camera_gear = cv2.VideoCapture(gear_port)

        time.sleep(1)

    if NETWORK_MODE:
        # This is the IP of the robo rio
        NetworkTable.setIPAddress(RIO_IP)
        NetworkTable.setClientMode()
        NetworkTable.initialize()

        # The name of the network table here needs to match the name in the java code
        sd = NetworkTable.getTable('Camera')

        time.sleep(1)

        # Initialize the values
        sd.putNumber('HG_Top_Area', -999)
        sd.putNumber('HG_Top_Ctr_X', -999)
        sd.putNumber('HG_Top_Ctr_Y', -999)
        sd.putNumber('HG_Bot_Area', -999)
        sd.putNumber('HG_Bot_Ctr_X', -999)
        sd.putNumber('HG_Bot_Ctr_Y', -999)

        sd.putNumber('Peg_Left_Area', -999)
        sd.putNumber('Peg_Left_Ctr_X', -999)
        sd.putNumber('Peg_Left_Ctr_Y', -999)
        sd.putNumber('Peg_Right_Area', -999)
        sd.putNumber('Peg_Right_Ctr_X', -999)
        sd.putNumber('Peg_Right_Ctr_Y', -999)

        # Reset the kill switch to 0
        heartbeat = 0
        sd.putNumber('Processing_On', 1)
        sd.putNumber('Heartbeat', heartbeat)

        if REALTIME_MODE:
            sd.putNumber('High_Goal_Port', high_goal_port)
            sd.putNumber('Gear_Port', gear_port)
            sd.putNumber('High_Goal_Cam_Found', high_goal_found)
            sd.putNumber('Gear_Cam_Found', gear_found)

    if REALTIME_MODE:
        while True:
            # Determine which camera we should be looking at
            # We still run the algorithm for both targets, as a safety if the cameras are
            # somehow switches
            if NETWORK_MODE:
                hg_logical = sd.getNumber('High_Goal_Logical', DEFAULT_HIGH_GOAL_CAM)

                if hg_logical == 1:
                    sd.putNumber('Peg_Left_Area', -999)
                    sd.putNumber('Peg_Left_Ctr_X', -999)
                    sd.putNumber('Peg_Left_Ctr_Y', -999)
                    sd.putNumber('Peg_Right_Area', -999)
                    sd.putNumber('Peg_Right_Ctr_X', -999)
                    sd.putNumber('Peg_Right_Ctr_Y', -999)

                    img = camera_hg.read()[1]
                    high_goal_ret_val = img_processing_main(img, True, False, DEBUG_TXT_FILES)
                    gear_ret_val = None
                else:
                    sd.putNumber('HG_Top_Area', -999)
                    sd.putNumber('HG_Top_Ctr_X', -999)
                    sd.putNumber('HG_Top_Ctr_Y', -999)
                    sd.putNumber('HG_Bot_Area', -999)
                    sd.putNumber('HG_Bot_Ctr_X', -999)
                    sd.putNumber('HG_Bot_Ctr_Y', -999)

                    img = camera_gear.read()[1]
                    gear_ret_val = img_processing_main(img, False, False, DEBUG_TXT_FILES)
                    high_goal_ret_val = None

                heartbeat += 0.0001
                sd.putNumber('Heartbeat', heartbeat)
            else:
                val = random.randint(0,1)
                if val:
                    img = camera_hg.read()[1]
                    high_goal_ret_val = img_processing_main(img, True, False, DEBUG_TXT_FILES)
                    gear_ret_val = None
                else:
                    img = camera_gear.read()[1]
                    gear_ret_val = img_processing_main(img, False, False, DEBUG_TXT_FILES)
                    high_goal_ret_val = None

            # Analyze the return parameters
            if high_goal_ret_val is None:
                print "High Goal Not Found"
            else:

                print "HG Top Area: " + str(high_goal_ret_val['top_area'])
                print "HG Top Ctr X: " + str(high_goal_ret_val['top_ctr_X'])
                print "HG Top Ctr Y: " + str(high_goal_ret_val['top_ctr_Y'])

                print "HG Bot Area: " + str(high_goal_ret_val['bot_area'])
                print "HG Bot Ctr X: " + str(high_goal_ret_val['bot_ctr_X'])
                print "HG Bot Ctr Y: " + str(high_goal_ret_val['bot_ctr_Y'])

                if NETWORK_MODE:
                    sd.putNumber('HG_Top_Area', high_goal_ret_val['top_area'])
                    sd.putNumber('HG_Top_Ctr_X', high_goal_ret_val['top_ctr_X'])
                    sd.putNumber('HG_Top_Ctr_Y', high_goal_ret_val['top_ctr_Y'])
                    sd.putNumber('HG_Bot_Area', high_goal_ret_val['bot_area'])
                    sd.putNumber('HG_Bot_Ctr_X', high_goal_ret_val['bot_ctr_X'])
                    sd.putNumber('HG_Bot_Ctr_Y', high_goal_ret_val['bot_ctr_Y'])

            if gear_ret_val is None:
                print "Peg Not Found"
            else:

                print "Peg Left Area: " + str(gear_ret_val['left_area'])
                print "Peg Left Ctr X: " + str(gear_ret_val['left_ctr_X'])
                print "Peg Left Ctr Y: " + str(gear_ret_val['left_ctr_Y'])

                print "Peg Right Area: " + str(gear_ret_val['right_area'])
                print "Peg Right Ctr X: " + str(gear_ret_val['right_ctr_X'])
                print "Peg Right Ctr Y: " + str(gear_ret_val['right_ctr_Y'])

                if NETWORK_MODE:
                    sd.putNumber('Peg_Left_Area', gear_ret_val['left_area'])
                    sd.putNumber('Peg_Left_Ctr_X', gear_ret_val['left_ctr_X'])
                    sd.putNumber('Peg_Left_Ctr_Y', gear_ret_val['left_ctr_Y'])
                    sd.putNumber('Peg_Right_Area', gear_ret_val['right_area'])
                    sd.putNumber('Peg_Right_Ctr_X', gear_ret_val['right_ctr_X'])
                    sd.putNumber('Peg_Right_Ctr_Y', gear_ret_val['right_ctr_Y'])

            if DISPLAY_IMAGE:
                cv2.imshow('Img', img)
                cv2.waitKey(1)

            # If in network mode, command to stop the image processing
            if NETWORK_MODE:
                kill_switch = sd.getNumber('Kill_Switch', 0)
                if kill_switch == 1:
                    # Return back to the shell script, which will then shutdown the jetson
                    sd.putNumber('Processing_On', -1)
                    time.sleep(1)
                    if ALLOW_SHUTDOWN:
                        os.system('echo ubuntu | sudo -S /sbin/shutdown -h now')
                    time.sleep(1)
                    return

    else:
        # For debugging purposes
        img = cv2.imread('test_6.png')

        (peg_ret_val, high_goal_ret_val) = img_processing_main(img, True, False)

        if peg_ret_val is None:
            print "Peg Not Found"
        else:
            print "Peg Found, parameters:"
            print peg_ret_val

        if high_goal_ret_val is None:
            print "High Goal Not Found"
        else:
            print "High Goal Found, parameters:"
            print high_goal_ret_val

if __name__ == "__main__":
    main()
