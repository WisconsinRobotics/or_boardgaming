import numpy as np
import cv2, os, time, scipy
from constants import *

class Generic_Board_Game_CV:
    def __init__(self, board_dims, initial_image, piece_diff_method, piece_values, debug = False):
        self.board_dims = board_dims
        self.debug = debug

        self.piece_diff_method = piece_diff_method
        self.piece_values = piece_values

        self.bsize = (BOARD_SQUARE_SIZE * 100, BOARD_SQUARE_SIZE * 100)

        self.BOARD = np.full(self.board_dims, '')
        corners = self.determine_board_corners_3(initial_image)
        self.M = self.compute_perspective_transform_matrix(corners)


    def reset_board(self):
        self.BOARD = np.full(self.board_dims, '')


    def update_board_state(self, frame, reinitialize = False):
        # recompute M if board moves significantly
        if reinitialize:
            corners = self.determine_board_corners_3(frame)
            self.M = self.compute_perspective_transform_matrix(corners)

        board_img = cv2.warpPerspective(frame, self.M, (self.bsize[0], self.bsize[1]))

        piece_locs = self.detect_game_pieces(board_img)
        for player, loc in piece_locs.items():
            if self.BOARD[loc] not in ['', self.piece_values[player]['label']]:
                print('possible error?')
            self.BOARD[loc] = self.piece_values[player]['label']


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
            [self.bsize[0] - 1, 0],
            [self.bsize[0] - 1, self.bsize[1] - 1],
            [0, self.bsize[1] - 1]
        ])
        # reorder corners if not in correct order
        ordered_corners = self.fix_corner_order(corners)
        # get M
        M = cv2.getPerspectiveTransform(ordered_corners, actual_dims)
        return M
    
    def detect_game_pieces(self, frame):
        pieceLocs = {}
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        cell_size = (self.bsize[0] // self.board_dims[0], self.bsize[1] // self.board_dims[1])

        for player in self.piece_values:
            locations = []

            # filter to players color
            lower_color, upper_color = self.piece_values[player]['color_values']
            mask = cv2.inRange(hsvFrame, lower_color, upper_color)
            mask = cv2.dilate(mask, np.ones((5, 5), "uint8"))
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # loop through each contour and add each valid contour
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 300:
                    moments = cv2.moments(contour)
                    if moments['m00'] == 0:
                        continue
                    new_loc = [
                        max(0, min(self.bsize[0] - 1, int(moments['m10'] / moments['m00']))),
                        max(0, min(self.bsize[1] - 1, int(moments['m01'] / moments['m00']))),
                    ]

                    # if shape filter enabled - filter out contours that dont match the shape
                    if self.piece_diff_method == 'shape':
                        all_shape_scores = []
                        curr_player_idx = list(self.piece_values).index(player)
                        for shape_player in self.piece_values:
                            ref = self.piece_values[shape_player]['shape_values']
                            score = cv2.matchShapes(contour, ref, cv2.CONTOURS_MATCH_I2, 0.0)
                            all_shape_scores.append(score)
                        best_score_idx = np.argmin(all_shape_scores)
                        if ((all_shape_scores[best_score_idx] >= 0.25) or (best_score_idx != curr_player_idx)):
                            continue

                    locations.append(new_loc)

            # discretize the locations
            pieceLocs[player] = []
            for loc in locations:
                new_loc = [
                    loc[0] // cell_size[0],
                    loc[1] // cell_size[1]
                ]
                if loc not in pieceLocs[player]:
                    pieceLocs[player].append(loc)

        return pieceLocs

    # def detect_game_pieces_by_color(self, hsvFrame, color_values):
    #     pieceLocs = {}
    #     for player in color_values:
    #         pieceLocs[player] = []

    #         lower_color, upper_color =  color_values[player]
    #         mask = cv2.inRange(hsvFrame, lower_color, upper_color)
    #         mask = cv2.dilate(mask, np.ones((5, 5), "uint8"))
    #         contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #         for i, contour in enumerate(contours):
    #             area = cv2.contourArea(contour)
    #             if area > 1000:
    #                 x, y, w, h = cv2.boundingRect(contour)
    #                 #imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #                 new_loc = [(x + w // 2), (y + h // 2)]
    #                 if True:
    #                     flag = False
    #                     for loc in pieceLocs[player]:
    #                         if np.linalg.norm([loc[0] - new_loc[0], loc[1] - new_loc[1]]) < 100:
    #                             flag = True
    #                             break
    #                     if not flag:
    #                         pieceLocs[player].append(new_loc)#'x': x, 'y': y, 'w': w, 'h': h})
    #                 else:
    #                     pieceLocs[player].append(new_loc)

    #     return pieceLocs

    # def detect_game_pieces_by_shape(self, frame):
    #     pieceLocs = {}
    #     for player in shape_templates:
    #         pieceLocs[player] = []


    #     mask = cv2.inRange(hsvFrame, lower_color, upper_color)
    #     mask = cv2.dilate(mask, np.ones((5, 5), "uint8"))
    #     contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #     for i, contour in enumerate(contours):
    #         area = cv2.contourArea(contour)
    #         if area > 1000:
    #             x, y, w, h = cv2.boundingRect(contour)
    #             #imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #             new_loc = [(x + w // 2), (y + h // 2)]
    #             if True:
    #                 flag = False
    #                 for loc in pieceLocs:
    #                     if np.linalg.norm([loc[0] - new_loc[0], loc[1] - new_loc[1]]) < 100:
    #                         flag = True
    #                         break
    #                 if not flag:
    #                     pieceLocs.append(new_loc)#'x': x, 'y': y, 'w': w, 'h': h})
    #             else:
    #                 pieceLocs.append(new_loc)

    #     return pieceLocs

    # def get_game_piece_locations(self, board_img):
    #     hsvFrame = cv2.cvtColor(board_img, cv2.COLOR_BGR2HSV)

    #     piece_locs = self.detect_game_pieces_by_color(hsvFrame, orange_lower, orange_upper)

    #     # discretize and
    #     final_piece_locs = []
    #     for loc in piece_locs:
    #         if loc not in final_piece_locs:
    #             final_piece_locs.append(loc)

    #     return final_piece_locs





# sample usage
def main():
    img = None
    orange_lower = np.array([10, 140, 140], np.uint8)
    orange_upper = np.array([25, 255, 255], np.uint8)
    cv_obj = Generic_Board_Game_CV(
        board_dims = (3, 3),
        initial_image = img,
        piece_diff_method = 'color',
        piece_values = {
            'robot': {
                'label': 'x',
                'color_values': [orange_lower, orange_upper],
                'shape_values': 'oval'
            },
            'human': {
                'label': 'o',
                'color_values': [orange_lower, orange_upper],
                'shape_values': 'oval'
            }
        },
        debug = False
    )

    

    

    
    
    
    



















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


