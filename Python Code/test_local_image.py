import cv2

from detect_u_shapes import find_u_shapes

img = cv2.imread('filename.png')

(all_u_shapes,all_u_shapes_parameters) = find_u_shapes(img,True)