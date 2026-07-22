import numpy as np
import matplotlib.pyplot as plt
import cv2, os, time, scipy
from constants import *

class Generic_Board_Game_CV:
    def __init__(self, board_dims, initial_image, piece_diff_method, piece_values, debug = False):
        self.board_dims = board_dims
        self.debug = debug

        self.piece_diff_method = piece_diff_method
        self.piece_values = piece_values

        self.bsize = (BOARD_SQUARE_SIZE[0] * 100, BOARD_SQUARE_SIZE[1] * 100)

        self.BOARD = np.full(self.board_dims, '')
        self.update_board_state(initial_image, reinitialize = True)


    def reset_board(self):
        self.BOARD = np.full(self.board_dims, '')

    def get_board(self):
        return self.BOARD

    def update_board_state(self, frame, reinitialize = False):
        # recompute M if board moves significantly
        if reinitialize:
            corners = self.determine_board_corners_3(frame)
            self.M = self.compute_perspective_transform_matrix(corners)

        board_img = cv2.warpPerspective(frame, self.M, (self.bsize[0], self.bsize[1]))

        piece_locs = self.detect_game_pieces(board_img)
        for player, locs in piece_locs.items():
            # if self.BOARD[loc] not in ['', self.piece_values[player]['label']]:
            #     print('possible error?')
            for loc in locs:
                self.BOARD[loc[1], loc[0]] = self.piece_values[player]['label']

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
                if new_loc not in pieceLocs[player]:
                    pieceLocs[player].append(new_loc)
            if len(pieceLocs[player]) == 0:
                pieceLocs.pop(player, None)

        return pieceLocs



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

def generate_shape_template(shape_name, shape_img = None):
    if shape_img is None:
        template_size = 200
        res = np.zeros((template_size, template_size), dtype = np.uint8)
        if shape_name == 'oval':
            cv2.ellipse(res, (template_size // 2, template_size // 2), (75, 40), 0, 0, 360, 255, -1)
        elif shape_name == 'cross':
            cv2.rectangle(res, (template_size // 2 - 20, 20), (template_size // 2 + 20, template_size - 20), 255, -1)
            cv2.rectangle(res, (20, template_size // 2 - 20), (template_size - 20, template_size // 2 + 20), 255, -1)
            res = cv2.warpAffine(
                res,
                cv2.getRotationMatrix2D((template_size // 2, template_size // 2), 45, 1.0),
                (template_size, template_size)
            )

    else:
        _, res = cv2.threshold(shape_img, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours[0]



# sample usage
def main():
    imgs = list(filter(lambda x: x.endswith('jpg'), os.listdir('..')))

    for i in imgs:
        board_img = cv2.imread(f'../{i}')
        robot_shape_img = cv2.imread(f'../oval_template.png', 0)

        orange_lower = np.array([10, 140, 140], np.uint8)
        orange_upper = np.array([25, 255, 255], np.uint8)
        cyan_lower = np.array([85, 140, 140], np.uint8)
        cyan_upper = np.array([100, 255, 255], np.uint8)

        cv_obj = Generic_Board_Game_CV(
            board_dims = (3, 3),
            initial_image = board_img,
            piece_diff_method = 'color',
            piece_values = {
                'robot': {
                    'label': 'o',
                    'color_values': [orange_lower, orange_upper],
                    'shape_values': generate_shape_template('oval', shape_img = robot_shape_img)
                },
                'human': {
                    'label': 'x',
                    'color_values': [cyan_lower, cyan_upper],
                    'shape_values': generate_shape_template('cross')
                }
            },
            debug = False
        )
        print(cv_obj.BOARD)
        plt.imshow(board_img)
        plt.show()

# main()

