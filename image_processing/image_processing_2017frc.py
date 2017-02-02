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

# Rectangle approx factors
MAX_AREA_DIFF = 3
MAX_PERI_DIFF = 1.5
MIN_PERI_DIFF = 0.5

# Constants for green
LOWER_GREEN = np.array([60, 190, 100])
UPPER_GREEN = np.array([80, 255, 255])


def calc_height_width(contour):
    leftmost = tuple(contour[contour[:,:,0].argmin()][0])
    rightmost = tuple(contour[contour[:,:,0].argmax()][0])
    topmost = tuple(contour[contour[:,:,1].argmin()][0])
    bottommost = tuple(contour[contour[:,:,1].argmax()][0])
    
    height = bottommost[1] - topmost[1]
    width = rightmost[0] - leftmost[0]
    
    return (height, width)
                          
def find_pegs(img, debug_mode, debug_file):
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
            cv2.drawContours(img,[box],0,(255,255,0),2)
            
            # should have larger height than width
            (height, width) = calc_height_width(contour)
            
            if width >= height:
                continue
                   
            # If we are here, shape is good
            saved_contour.append(contour)
            cv2.drawContours(img, [contour], 0, (0, 0, 255), 2)
            
        
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
            with open(DEBUG_FILEPATH + 'logfile_found.txt', 'a+') as f:
                f.write(str(ret_val['left_area']) + ', ' +
                        str(ret_val['left_ctr_X']) + ', ' +
                        str(ret_val['left_ctr_Y']) + ', ' +
                        str(ret_val['right_area']) + ', ' +
                        str(ret_val['right_ctr_X']) + ', ' +
                        str(ret_val['right_ctr_Y']) + '\n')
    else:
        # Have 1 or less contour, which means we did not detect the shape
        if debug_file:
            with open(DEBUG_FILEPATH + 'logfile_notfound.txt', 'a+') as f:
                f.write(".")
        return (None, img)
        
    return (ret_val, img)

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
        
        area = cv2.contourArea(contour) 
        peri = cv2.arcLength(contour, True) 

        # Only consider the "larger" contours
        if peri > MIN_PERIMETER and area > MIN_AREA:
            
            # Validate the contour makes sense
            rect = cv2.minAreaRect(contour)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(img,[box],0,(255,255,0),2)
            
            rect_area = cv2.contourArea(box)
            rect_peri = cv2.arcLength(box, True)
            
            # Area of the bounding rectangle will always be bigger
            # than the actial object.  Make sure its not too much bigger
            area_good = rect_area/area < MAX_AREA_DIFF
            peri_good = (rect_peri/peri < MAX_PERI_DIFF) and (rect_peri/peri > MIN_PERI_DIFF)
            
            if (not area_good) | (not peri_good):
                continue
            
            # should have larger width than height
            (height, width) = calc_height_width(contour)
            
            if height >= width:
                continue
        
            # If we are here, shape is good
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
        # Have 1 or less contour, which means we did not detect the shape
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
        img = cv2.imread('peg1.png')
        #img = cv2.imread('test_1.png')
        
        #(ret_val, img) = find_rectagles(img, True, False)
        (ret_val, img) = find_pegs(img, True, False)
        
        if ret_val is None:
            print "Not Found"
        else:
        
            print ret_val
#            print "Top Area: " + str(ret_val['top_area'])
#            print "Top Ctr X: " + str(ret_val['top_ctr_X'])
#            print "Top Ctr Y: " + str(ret_val['top_ctr_Y'])
#            
#            print "Bot Area: " + str(ret_val['bot_area'])
#            print "Bot Ctr X: " + str(ret_val['bot_ctr_X'])
#            print "Bot Ctr Y: " + str(ret_val['bot_ctr_Y'])
        
    
