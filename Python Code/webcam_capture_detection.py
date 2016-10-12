
import cv2

from detect_u_shapes import find_u_shapes

camera_port = 1
camera = cv2.VideoCapture(camera_port)

# Designed to be ran with the MS LifeCam HD 3000

# Set true if the OS is windows
windows = True

if windows:
    # Windows can access these parameters, but linux cannot.
    # Need to use set these parameters with other means on linux
    camera.set(cv2.CAP_PROP_EXPOSURE,-11)
    camera.set(cv2.CAP_PROP_BRIGHTNESS,30)
    camera.set(cv2.CAP_PROP_CONTRAST,10)

while True:

    img = camera.read()[1]
     
    (all_u_shapes,all_u_shapes_parameters) = find_u_shapes(img,False)

    #Draw the U shape     
    for u_shape in all_u_shapes:                
        cv2.drawContours(img,[u_shape],0,(0,0,255),thickness = 2)
    
    if len(all_u_shapes) == 0:
        print "Not Found"
    else:
        print "Found"
        
        for u_shape_parameter in all_u_shapes_parameters:
            print "Center Width: " + str(u_shape_parameter[0][0]) + " Center Height: " + str(u_shape_parameter[0][1])
            print "Left Side Height: " + str(u_shape_parameter[1])
            print "Right Side Height: " + str(u_shape_parameter[2])
            print "Bottom Width: " + str(u_shape_parameter[3])
        
    cv2.imshow("Img", img)
    cv2.waitKey(1)
    
del(camera)