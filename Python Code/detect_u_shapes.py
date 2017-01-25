import numpy as np
import cv2
from scipy.spatial import distance
import math

# Height and width of the webcam's image
WIDTH = 640
HEIGHT = 480

# Min and max angle to count at "correct"
MIN_ANGLE = 70
MAX_ANGLE = 110

# Min perimeter for the object... use for optimization
MIN_PERIMETER = 30

# Height and width of the returned image
WIDTH = 640
HEIGHT = 480

# Approximation constant that is multiplied by perimeter
APPROX_POLYDP_FACTOR = 0.01

# Inner square sides must be at least this length
DIST_INNER_SQUARE_MIN = 10

# Top edges must have 50% diff at max
TOP_EDGES_FACTOR = 0.5

# Top edges must not be more than 20% of the length of the bottom width
TOP_EDGES_TO_BOTTOM = 0.2

# Used to ensure the inner box doesnt have any left over pixels
FUDGE_FACTOR = 3

# Constants for green
LOWER_GREEN = np.array([55, 130, 20])
UPPER_GREEN = np.array([85, 255, 255])

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

def find_u_shapes(img, debug_mode):
    '''
    Main method
    '''

    all_u_shapes = []
    all_u_shapes_parameters = []

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
    _, cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop thru all the contours identified in the picture
    for contour in cnts:

        # Approx contour to reduce the number of points
        peri = cv2.arcLength(contour, True)
        contour = cv2.approxPolyDP(contour, APPROX_POLYDP_FACTOR*peri, True)

        # Only consider the "larger" contours
        if peri > MIN_PERIMETER:

            # Calculate the outer 4 corner points
            (bot_left, bot_right, top_left, top_right) = find_corner_points(contour)

            # All angles should be around 90 deg
            bot_left_angle = angle(bot_left, top_left, bot_right)
            bot_right_angle = angle(bot_right, bot_left, top_right)
            top_left_angle = angle(top_left, bot_left, top_right)
            top_right_angle = angle(top_right, bot_right, top_left)

            if ((bot_left_angle > MIN_ANGLE and bot_left_angle < MAX_ANGLE) and
                (bot_right_angle > MIN_ANGLE and bot_right_angle < MAX_ANGLE) and
                (top_left_angle > MIN_ANGLE and top_left_angle < MAX_ANGLE) and
                (top_right_angle > MIN_ANGLE and top_right_angle < MAX_ANGLE)) == False:
                continue

            # Determine the enclosing box with the 4 corner points
            # Introduce a fudge factor to ensure the inner box is correct

            box = np.vstack((bot_left + np.array((FUDGE_FACTOR, -FUDGE_FACTOR)),
                             top_left + np.array((FUDGE_FACTOR, FUDGE_FACTOR)),
                             top_right + np.array((-FUDGE_FACTOR, FUDGE_FACTOR)),
                             bot_right + np.array((-FUDGE_FACTOR, -FUDGE_FACTOR))))

            top_left = top_left + np.array((0, FUDGE_FACTOR))
            top_right = top_right + np.array((0, FUDGE_FACTOR))

            if debug_mode:
                cv2.drawContours(img, [box], 0, (0, 0, 255), thickness=2)
                cv2.imshow("img", img)
                cv2.waitKey(0)

            # Create an image of the outer box
            inner_img = np.zeros((HEIGHT, WIDTH, 1), np.uint8)
            cv2.drawContours(inner_img, [box], 0, (255), thickness=cv2.FILLED)

            if debug_mode:
                cv2.imshow("box", inner_img)
                cv2.waitKey(0)

            # Exclude the U shape from the box, to make the inner box
            inner_img[mask > 1] = [(0)]

            if debug_mode:
                cv2.imshow("small_box", inner_img)
                cv2.waitKey(0)

            # Find contours in the inner box
            _, cnts_inner, _ = cv2.findContours(inner_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Look thru the contours, identify the sole one that is the inner box
            found_inner_box = False

            for c_inner in cnts_inner:

                peri = cv2.arcLength(c_inner, True)
                c_inner = cv2.approxPolyDP(c_inner, APPROX_POLYDP_FACTOR*peri, True)

                if peri > MIN_PERIMETER and len(c_inner) >= 4:
                    # Calculate the inner 4 corner points
                    (bot_left_inner, bot_right_inner, top_left_inner, top_right_inner) = find_corner_points(c_inner)

                    # All angles should be around 90 deg
                    bot_left_inner_angle = angle(bot_left_inner, top_left_inner, bot_right_inner)
                    bot_right_inner_angle = angle(bot_right_inner, bot_left_inner, top_right_inner)
                    top_left_inner_angle = angle(top_left_inner, bot_left_inner, top_right_inner)
                    top_right_inner_angle = angle(top_right_inner, bot_right_inner, top_left_inner)

                    if ((bot_left_inner_angle > MIN_ANGLE and bot_left_inner_angle < MAX_ANGLE) and
                        (bot_right_inner_angle > MIN_ANGLE and bot_right_inner_angle < MAX_ANGLE) and
                        (top_left_inner_angle > MIN_ANGLE and top_left_inner_angle < MAX_ANGLE) and
                        (top_right_inner_angle > MIN_ANGLE and top_right_inner_angle < MAX_ANGLE)) == False:
                        continue

                    # Each leg of the "square" must be at least a certain length
                    top_dist = distance.euclidean(top_left_inner, top_right_inner)
                    bot_dist = distance.euclidean(bot_left_inner, bot_right_inner)
                    left_side = distance.euclidean(top_left_inner, bot_left_inner)
                    right_side = distance.euclidean(top_right_inner, bot_right_inner)

                    if (top_dist < DIST_INNER_SQUARE_MIN or bot_dist < DIST_INNER_SQUARE_MIN
                        or left_side < DIST_INNER_SQUARE_MIN or right_side < DIST_INNER_SQUARE_MIN):
                        continue

                    #Once we find the box, stop looking thru the rest of the contours
                    found_inner_box = True
                    break

            # If no inner box, move onto the next potentiao U shape
            if found_inner_box == False:
                continue

            inner_box = np.vstack((bot_left_inner, top_left_inner, top_right_inner, bot_right_inner))

            if debug_mode:
                cv2.drawContours(img,[inner_box], 0, (0, 0, 255), thickness = 2)
                cv2.imshow("img", img)
                cv2.waitKey(0)

            # Create the total U shape image
            u_shape = np.vstack((top_left, bot_left, bot_right, top_right,
                                 top_right_inner, bot_right_inner, bot_left_inner, top_left_inner))

            # Check top edge distances are similar
            upper_left_dist = distance.euclidean(top_left,top_left_inner)
            upper_right_dist = distance.euclidean(top_right,top_right_inner)

            if (upper_left_dist < TOP_EDGES_FACTOR*upper_right_dist
                or upper_left_dist > (1.0/TOP_EDGES_FACTOR)*upper_right_dist):
                continue

            # Check that the top edges are much smaller than the bottom width
            bottom_dist = distance.euclidean(bot_left,bot_right)

            if (upper_left_dist > TOP_EDGES_TO_BOTTOM * bottom_dist
                or upper_right_dist > TOP_EDGES_TO_BOTTOM * bottom_dist):
                continue

            '''
            Calculate features to return
            '''

            left_side_dist = distance.euclidean(bot_left,top_left)
            right_side_dist = distance.euclidean(bot_right,top_right)

            M = cv2.moments(contour)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            center = np.array((cx,cy))

            # If still here, we want to add the shape
            all_u_shapes.append(u_shape)
            all_u_shapes_parameters.append((center, left_side_dist, right_side_dist, bottom_dist))

    return (all_u_shapes,all_u_shapes_parameters)
