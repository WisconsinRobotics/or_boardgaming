import numpy as np
import cv2, os, time

# strats
# pros of perspective transform
    # gives only board and eliminated all other noise/colors from background
    # thus creating a clean slate for color detection based detection of pieces
        # and also detect based on shapes
# cons
    # either needs recomputing every turn - doable n handles occlusion well but untested in diff lighting setups
    # if reused then can be really broken if board moves too significantly - tho should be able to handle slight movements


    # 1 - take pic of empty board to setup the perspective transform then reuse that
        # if board moves then it would kinda suck - but also 
    # 2 - detect piece positions exactly
        # 2.1 - then use the positions of pieces to "relative" guess which orientation it is
        #

# tasks:
    # look at the picture to get the board state
    # get perspective transform from board to get current location of 

def clickPicture(cap, count = 1, saveimg = False):
    res, frame = cap.read()
    if res:
        if saveimg:
            os.makedirs('../images/', exist_ok = True)
            cv2.imwrite(f'../images/img_{count}_{int(time.time())}.png', frame)
        return frame
    else:
        print(f'WARNING: Cant receive frame (stream end?). trying again. try {count}')
        if count < 3:
            time.sleep(0.2)
            return clickPicture(cap, count + 1, saveimg=saveimg)
        else:
            print('ERROR: camera error. pic not clicked even after 3 attempts. sadge')
            return None


class Tic_Tac_Toe_CV:
    BOARD = np.array([
        ['', '', ''],
        ['', '', ''],
        ['', '', ''],
    ])

    BOARD_SQUARE_SIZE = 2 # irl size of each square on board in inches

    def __init__(self, robot_piece = 'x'):
        self.ROBOT_PIECE = robot_piece
        self.reset_board()

    def reset_board(self):
        self.BOARD = np.array([
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
        ])

    def update_board(self, new_pos, new_piece):
        assert len(new_pos) == 2, 'invalid position'
        assert self.BOARD[new_pos] == '', 'position already occupied'
        self.BOARD[new_pos] = new_piece

    def getPerspectiveTransform(self, corners):
        actual_dims = np.float32([
            [0, 0],
            [self.BOARD_SQUARE_SIZE, 0],
            [0, self.BOARD_SQUARE_SIZE],
            [self.BOARD_SQUARE_SIZE, self.BOARD_SQUARE_SIZE]
        ])
        M = cv2.getPerspectiveTransform(corners, actual_dims)
        return M




def detect_locations(hsvFrame, lower_color, upper_color):
    pieceLocs = []
    mask = cv2.inRange(hsvFrame, lower_color, upper_color)
    kernel = np.ones((5, 5), "uint8")
    mask = cv2.dilate(mask, kernel)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            #imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            new_loc = [(x + w // 2), (y + h // 2)]
            if True:
                flag = False
                for loc in pieceLocs:
                    if np.linalg.norm([loc[0] - new_loc[0], loc[1] - new_loc[1]]) < 100:
                        flag = True
                        break
                if not flag:
                    pieceLocs.append(new_loc)#'x': x, 'y': y, 'w': w, 'h': h})
            else:
                pieceLocs.append(new_loc)

    return pieceLocs

def detectBoardPieceLocations(imageFrame):

    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)
    
    # Test the color limits to make sure they identify the blue and orange pieces
    orange_lower = np.array([10, 140, 140], np.uint8)
    orange_upper = np.array([25, 255, 255], np.uint8)
    blue_lower = np.array([110, 100, 100], np.uint8)
    blue_upper = np.array([160, 255, 255], np.uint8)
    
    pieceLocs = {}
    pieceLocs['orange'] = detect_locations(hsvFrame, orange_lower, orange_upper)
    pieceLocs['blue'] = detect_locations(hsvFrame, blue_lower, blue_upper)

    return pieceLocs

def determineBoardCorners(frame):
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ### getting contours in image ###
    # includes all values above 100
    # basically turns image into binary white/black depending on value
    ret,thresh = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)

    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    cnt = np.float32(contours[0])
    #v2.drawContours(frame, contours, -1, (0,255,0), 2)

    ### detects corners ###
    # right now only tracks 4 at a time i think
    corners = cv2.goodFeaturesToTrack(gray,40,0.01,10)
    corners = np.intp(corners) # array of corners?

    # # if corner is within board line contours, add it to board corner array
    # board_corners = []
    # for i in corners:
    #     x = int(i[0][0])
    #     y = int(i[0][1])
    #     dist = cv2.pointPolygonTest(cnt,(x,y),True)
    #     if dist:
    #         board_corners.append(i[0])

    # # finding min and max corners
    # max = [0,0]
    # min = [1000,1000]
    # for i in board_corners:
    #     x = int(i[0])
    #     y = int(i[1])
    #     if (x < min[0]) and (y < min[1]):
    #         min = i
    #     if(x > max[0]) and (y > max[1]):
    #         max = i

    # # calculating size of each square on board
    # width_x = max[0] - min[0]
    # height_y = max[1] - min[1]

    # # draws circle for each corner
    # for i in corners:
    #     x,y = i.ravel()
    #     cv2.circle(frame,(x,y),3,(0,0,255),-1)

    return np.float32(corners.reshape(40,2))


