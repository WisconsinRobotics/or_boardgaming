import numpy as np
import cv2 as cv

BOARD_SQUARE_SIZE = 2 # in inches

def determineBoardCorners(frame):
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    ### getting contours in image ###
    # includes all values above 100
    # basically turns image into binary white/black depending on value
    ret,thresh = cv.threshold(gray,100,255,cv.THRESH_BINARY)

    contours,hierarchy = cv.findContours(thresh, 1, 2)
    cnt = contours[0]
    cv.drawContours(frame, contours, -1, (0,255,0), 2)

    ### detects corners ###
    # right now only tracks 4 at a time i think
    corners = cv.goodFeaturesToTrack(gray,4,0.01,10)
    corners = np.intp(corners) # array of corners?

    # if corner is within board line contours, add it to board corner array
    board_corners = []
    for i in corners:
        x = int(i[0][0])
        y = int(i[0][1])
        dist = cv.pointPolygonTest(cnt,(x,y),True)
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
        cv.circle(frame,(x,y),3,(0,0,255),-1)

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