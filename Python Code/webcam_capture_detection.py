
import cv2

camera_port = 1
camera = cv2.VideoCapture(camera_port)

img = camera.read()[1]

cv2.imwrite('new_test2.png', img)
