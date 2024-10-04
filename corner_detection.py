import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
 
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read() # frame is an image
 
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
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
    if(corners.size > 1):
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
 
    # displays video
    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        break
 
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()