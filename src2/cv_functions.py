import numpy as np
import cv2

BOARD_SQUARE_SIZE = 2 # in inches


def detectBoardPieceLocations(imageFrame):

    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    orange_lower = np.array([10, 140, 140], np.uint8)
    orange_upper = np.array([25, 255, 255], np.uint8)
    orange_mask = cv2.inRange(hsvFrame, orange_lower, orange_upper)

    kernel = np.ones((5, 5), "uint8")

    orange_mask = cv2.dilate(orange_mask, kernel)
    res_orange = cv2.bitwise_and(imageFrame, imageFrame, mask=orange_mask) # not quite sure what this is for

    contours, hierarchy = cv2.findContours(orange_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    pieceLocs = []
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 1000: # not sure what the 1000 logic is but will figure out when testing ig
            x, y, w, h = cv2.boundingRect(contour)
            imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # if game_board["b2"][1][0] > (x + 35) > game_board["b2"][0][0]:
            #     print("O PLACED HERE")

            pieceLocs.append({'x': x, 'y': y, 'w': w, 'h': h})

    return pieceLocs

def determineBoardCorners(frame):
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ### getting contours in image ###
    # includes all values above 100
    # basically turns image into binary white/black depending on value
    ret,thresh = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)

    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    cnt = contours[0]
    cv2.drawContours(frame, contours, -1, (0,255,0), 2)

    ### detects corners ###
    # right now only tracks 4 at a time i think
    corners = cv2.goodFeaturesToTrack(gray,4,0.01,10)
    corners = np.intp(corners) # array of corners?

    # if corner is within board line contours, add it to board corner array
    board_corners = []
    for i in corners:
        x = int(i[0][0])
        y = int(i[0][1])
        dist = cv2.pointPolygonTest(cnt,(x,y),True)
        if dist:
            board_corners.append(i[0])

    # finding min and max corners
    max = [0,0]
    min = [1000,1000]
    for i in board_corners:
        x = int(i[0])
        y = int(i[1])
        if (x < min[0]) and (y < min[1]):
            min = i
        if(x > max[0]) and (y > max[1]):
            max = i

    # calculating size of each square on board
    width_x = max[0] - min[0]
    height_y = max[1] - min[1]

    # draws circle for each corner
    for i in corners:
        x,y = i.ravel()
        cv2.circle(frame,(x,y),3,(0,0,255),-1)

    return {
        'w': width_x,
        'h': height_y,
        'corners': corners # [[3, 2], [2, 5], [2, 4], [9, 7]]
    }

# this will make the assumption that
# a - the board corners are in order, i.e., fix the board corners function to make it that
# b - there r only 4 board corners
# c - not only r they ordered they r arranged as top-left, top-right, bottom-right, bottom-left - 
#       y? cuz i need smth i can work with n im alr putting a lot of faith in this working perfectly
# d - the width and height are what they claim - they rnt but also they can be kept consistent rather easily 
#       so words being off is technically not the end of the world

def determineBoardLocations(d):
    b = np.zeros((3, 3, 2))
    top_left, bottom_right, bottom_left, top_right = d['corners']
    b[0][0] = top_left[0] - (d['width_x'] / 2), top_left[1] - (d['height_y'] / 2)
    #b[0][0] = (corner[0][0] - (width_x // 2), corner[0][1] - (height_y // 2) )
    #b[0][1] = (corner[0][0] - (width_x // 2), corner[0][1] - (height_y // 2) )
    # center = mid point of all corners
    # (corner[0] + (width_x // 2) = 
    pass