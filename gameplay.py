import cv2
import numpy as np
import os, time
from corner_detection import determineBoardCorners
from color_detection import detectBoardPieceLocations

def errorHandle(s = 'default error message'):
    # print error message in console
    print('Error:', s)
    # do LED red flashing or smth
    # make sad sound
    # exit

def clickPicture(cap, count = 1, saveimg = False):
    res, frame = cap.read()
    if res:
        if saveimg:
            os.makedirs('./images/', exist_ok = True)
            cv2.imwrite(f'./images/img_{count}_{int(time.time())}.png', frame)
        return frame
    else:
        print(f'Cant receive frame (stream end?). trying again. try {count}')
        if count < 3:
            time.sleep(0.2)
            return clickPicture(cap, count + 1, saveimg=saveimg)
        else:
            errorHandle('camera error. pic not clicked even after 3 attempts. sadge')
            return None

def boardSetup():
    frame = clickPicture()
    if frame is None:
        errorHandle('Picture not clicked')
    boardVals = determineBoardCorners(frame)

    # placeholder
    board = np.zeros((3, 3))
    return board

# colors:
# blue blinking - bot turn start - computing best move n waypoints
# yellow blinking - actual moving
# green solid - bot turn end - human move
# red blinking - error - usually fatal

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        errorHandle('Cannot open camera')

    cap.release()
    cv2.destroyAllWindows()
    