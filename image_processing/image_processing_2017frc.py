import numpy as np
import cv2
import math
from networktables import NetworkTable


DEBUG_FILEPATH = '/home/ubuntu/Documents/FIRST_Image_Processing/image_processing/'

# Min perimeter for the object... use for optimization
MIN_PERIMETER = 50
MIN_AREA = 200

# Height and width of the returned image
WIDTH = 640
HEIGHT = 480

# Approximation constant that is multiplied by perimeter
APPROX_POLYDP_FACTOR = 0.01

# Functional logicals
REALTIME_MODE = False
NETWORK_MODE = False
DISPLAY_IMAGE = True

# Constants for green
LOWER_GREEN = np.array([60, 190, 100])
UPPER_GREEN = np.array([80, 255, 255])

def find_corner_points(contour):
    '''
    Finds the four corner points of a given contour
    '''
    contour = contour.squeeze()

    bot_left_diff = np.sum((contour - np.array([0, HEIGHT]))**2, axis=1)
    bot_left_index = np.argmin(bot_left_diff)
    bot_left = contour[bot_left_index, :]

    bot_right_diff = np.sum((contour - np.array([WIDTH, HEIGHT]))**2, axis=1)
    bot_right_index = np.argmin(bot_right_diff)
    bot_right = contour[bot_right_index, :]

    top_left_diff = np.sum((contour - np.array([0, 0]))**2, axis=1)
    top_left_index = np.argmin(top_left_diff)
    top_left = contour[top_left_index, :]

    top_right_diff = np.sum((contour - np.array([WIDTH, 0]))**2, axis=1)
    top_right_index = np.argmin(top_right_diff)
    top_right = contour[top_right_index, :]

    return (bot_left, bot_right, top_left, top_right)

def angle(pt0, pt1, pt2):
    '''
    Retuns the angle between three points
    '''
    dx1 = long(pt1[0] - pt0[0])
    dy1 = long(pt1[1] - pt0[1])
    dx2 = long(pt2[0] - pt0[0])
    dy2 = long(pt2[1] - pt0[1])

    return math.degrees(math.acos((dx1*dx2 + dy1*dy2)/
                                  math.sqrt((dx1**2 + dy1**2)*(dx2**2+ dy2**2) + 1e-10)))

def find_rectagles(img, debug_mode, debug_file):
    '''
    Main method
    '''

    if debug_mode:
        cv2.imshow("img", img)
        cv2.waitKey(0)

    # Blur, the convert to hsv
    img = cv2.GaussianBlur(img, (3, 3), 0)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Determine where the green pixels are
    mask = cv2.inRange(hsv_img, LOWER_GREEN, UPPER_GREEN)

    if debug_mode:
        cv2.imshow("mask", mask)
        cv2.waitKey(0)

    # find contours among the mask
    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

    # Loop thru all the contours identified in the picture
    top_obj = None
    bot_obj = None
    ret_val = {}
    saved_contour = []
    for contour in cnts:
        
        peri = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour) 

        # Only consider the "larger" contours
        if peri > MIN_PERIMETER and area > MIN_AREA:
            saved_contour.append(contour)
            cv2.drawContours(img, [contour], 0, (0, 0, 255), 2)
    
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
            with open(DEBUG_FILEPATH + 'logfile_found.txt', 'a+') as f:
                f.write(str(ret_val['top_area']) + ', ' +
                        str(ret_val['top_ctr_X']) + ', ' +
                        str(ret_val['top_ctr_Y']) + ', ' +
                        str(ret_val['bot_area']) + ', ' +
                        str(ret_val['bot_ctr_X']) + ', ' +
                        str(ret_val['bot_ctr_Y']) + '\n')
    else:
        if debug_file:
            with open(DEBUG_FILEPATH + 'logfile_notfound.txt', 'a+') as f:
                f.write(".")
        return (None, img)
        
    return (ret_val, img)
    
if __name__ == "__main__":
    
    if REALTIME_MODE:
        camera_port = 0
        camera = cv2.VideoCapture(camera_port)
    
    if NETWORK_MODE:
        # This is the IP of the robo rio
        NetworkTable.setIPAddress('10.13.27.22')
        NetworkTable.setClientMode()
        NetworkTable.initialize()
        
        # The name of the network table here needs to match the name in the java code
        sd = NetworkTable.getTable('Camera')
    
    if REALTIME_MODE:
        while True:
            img = camera.read()[1]
            (ret_val, img) = find_rectagles(img, False, True)
            
            if ret_val is None:
                print "Not Found"
            else:
        
                print "Top Area: " + str(ret_val['top_area'])
                print "Top Ctr X: " + str(ret_val['top_ctr_X'])
                print "Top Ctr Y: " + str(ret_val['top_ctr_Y'])
                
                print "Bot Area: " + str(ret_val['bot_area'])
                print "Bot Ctr X: " + str(ret_val['bot_ctr_X'])
                print "Bot Ctr Y: " + str(ret_val['bot_ctr_Y'])
                
            if NETWORK_MODE:
                sd.putNumber('Top_Area', ret_val['top_area'])
                sd.putNumber('Top_Ctr_X', ret_val['top_ctr_X'])
                sd.putNumber('Top_Ctr_Y', ret_val['top_ctr_Y'])
                sd.putNumber('Bot_Area', ret_val['bot_area'])
                sd.putNumber('Bot_Ctr_X', ret_val['bot_ctr_X'])
                sd.putNumber('Bot_Ctr_Y', ret_val['bot_ctr_Y'])
                
            if DISPLAY_IMAGE:
                cv2.imshow('Img', img)
                cv2.waitKey(1)

    else:
        # For debugging purposes
        img = cv2.imread('test_10.png')
        
        (ret_val, img) = find_rectagles(img, True, False)
        
        if ret_val is None:
            print "Not Found"
        else:
        
            print "Top Area: " + str(ret_val['top_area'])
            print "Top Ctr X: " + str(ret_val['top_ctr_X'])
            print "Top Ctr Y: " + str(ret_val['top_ctr_Y'])
            
            print "Bot Area: " + str(ret_val['bot_area'])
            print "Bot Ctr X: " + str(ret_val['bot_ctr_X'])
            print "Bot Ctr Y: " + str(ret_val['bot_ctr_Y'])
        
    
