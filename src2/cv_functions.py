import numpy as np
import cv2, os, time, scipy
from constants import *

class Generic_Board_Game_CV:
    def __init__(self, robot_piece, human_piece, board_dims, initial_image, debug = False):
        self.ROBOT_PIECE = robot_piece
        self.HUMAN_PIECE = human_piece

        self.board_dims = board_dims
        self.BOARD = np.full(self.board_dims, '')
        self.debug = debug

        self.bsize = BOARD_SQUARE_SIZE * 100

        corners = self.determine_board_corners_3(initial_image)
        self.M = self.compute_perspective_transform_matrix(corners)


    def reset_board(self):
        self.BOARD = np.full(self.board_dims, '')

    # def update_board(self, new_pos, new_piece):
    #     assert len(new_pos) == 2, 'invalid position'
    #     assert self.BOARD[new_pos] == new_piece, 'position already occupied'

    #     self.BOARD[new_pos] = new_piece
    #     if self.debug:
    #         print(f'Piece {new_piece} added to board position {new_pos}')

    
    def update_board_state(self, frame, reinitialize = False):
        # recompute M if board moves significantly
        if reinitialize:
            corners = self.determine_board_corners_3(frame)
            self.M = self.compute_perspective_transform_matrix(corners)

        board_img = cv2.warpPerspective(frame, self.M, (self.bsize, self.bsize))
        
        piece_locs = []
        for loc in piece_locs:
            self.BOARD[loc] = self.ROBOT_PIECE

    


    

    def determine_board_corners_3(self, frame, outlier_thresh = 1.5):
        num_corners = (self.board_dims[0] + 1) * (self.board_dims[1] + 1)

        # make it greyscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray,50,255,cv2.THRESH_BINARY)

        # find the biggest contour and make that into a mask (should filter it to only the board)
        contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_contour = max(contours, key = cv2.contourArea)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [max_contour], -1, 255, -1)

        # find best features (ie points) in the masked greyscale image
        corners = cv2.goodFeaturesToTrack(gray, num_corners, 0.01, 10, mask = mask)
        corners = np.float32(np.intp(corners).reshape(num_corners, 2))

        # filter out outliers
        filtered_corners = self.filter_outliers_2(corners, thresh = outlier_thresh)

        # get bounding points
        if True:
            final_corners = np.float32(cv2.boxPoints(cv2.minAreaRect(filtered_corners)))
        else:
            hull = cv2.convexHull(filtered_corners)
            epsilon = 0.04 * cv2.arcLength(hull, closed = True)
            final_corners = cv2.approxPolyDP(hull, epsilon, closed = True).reshape(-1, 2)

        # TODO - use bounding lines instead

        return final_corners
    
    def filter_outliers_2(self, corners, thresh = 1.5):
        '''
        filter out the outliers in the points detected on the board
        '''
        # using kdtree to get 3rd nearest neighbor n if its too far away then filter it out
        # will filter out any scattered outliers and upto {clustered_outlier_count_thresh} clustered outliers
        # ie so say clustered_outlier_count_thresh = 3, and there are 3 outliers that are really close to each other
        # but are otherwise far away from every other point in the grid, they will still get filtered out

        # cannot be higher than (n1 + n2 + 1) for n1,n2 = dim of points in grid
        # so for tictactoe thats 4 + 4 + 1 = 9
        # 4 is a good default value
        clustered_outlier_count_thresh = 4
        assert clustered_outlier_count_thresh < ((self.board_dims[0] + 1 + self.board_dims[1] + 1) + 1)
        if len(corners) < 4:
            return corners

        tree = scipy.spatial.KDTree(corners)
        distances, _ = tree.query(corners, k = clustered_outlier_count_thresh)
        nearest_pt_dist = distances[:, clustered_outlier_count_thresh - 1]
        non_outlier_mask = nearest_pt_dist < (thresh * np.median(nearest_pt_dist))
        return corners[non_outlier_mask]

    def fix_corner_order(self, corners):
        # sort corners by angle from center
        cx, cy = np.mean(corners, axis = 0)
        angles = np.arctan2(corners[:, 1] - cy, corners[:, 0] - cx)
        ordered_corners = corners[np.argsort(angles)]
        # using np roll to start with top left
        return np.roll(ordered_corners, -np.argmin(np.sum(ordered_corners, axis = 1)), axis = 0).astype('float32')

    def compute_perspective_transform_matrix(self, corners):
        actual_dims = np.float32([
            [0, 0],
            [self.bsize - 1, 0],
            [self.bsize - 1, self.bsize - 1],
            [0, self.bsize - 1]
        ])
        # reorder corners if not in correct order
        ordered_corners = self.fix_corner_order(corners)
        # get M
        M = cv2.getPerspectiveTransform(ordered_corners, actual_dims)
        return M

    def detect_game_pieces(self, hsvFrame, lower_color, upper_color):
        pieceLocs = []
        mask = cv2.inRange(hsvFrame, lower_color, upper_color)
        mask = cv2.dilate(mask, np.ones((5, 5), "uint8"))
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

    def get_game_piece_locations(self, board_img):
        hsvFrame = cv2.cvtColor(board_img, cv2.COLOR_BGR2HSV)
        orange_lower = np.array([10, 140, 140], np.uint8)
        orange_upper = np.array([25, 255, 255], np.uint8)

        piece_locs = self.detect_game_piece(hsvFrame, orange_lower, orange_upper)

        # discretize and
        final_piece_locs = []
        for loc in piece_locs:
            if loc not in final_piece_locs:
                final_piece_locs.append(loc)

        return final_piece_locs 






class Tic_Tac_Toe_CV:

    def __init__(self, robot_piece = 'x', debug = False):
        self.ROBOT_PIECE = robot_piece
        self.board_dims = (3, 3)
        self.BOARD = np.full(self.board_dims, ' ')
        self.debug = debug


    def reset_board(self):
        self.BOARD = np.full(self.board_dims, ' ')

    

    

    
    
    
    



















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


