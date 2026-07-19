import cv2, os, time
import numpy as np
from tic_tac_toe_logic_v2 import tic_tac_toe_logic_v2, check_win_condition
from path_planning import find_and_execute_path
# from hardware_setup import *
from cv_functions import *

ROBOT_PIECE = 'o'
HUMAN_PIECE = 'x'
imgs = list(filter(lambda x: x.endswith('jpg'), os.listdir('..')))

# colors:
# blue blinking - bot turn start - computing best move n waypoints
# yellow blinking - actual moving - humans beware
# green solid - bot turn end - human move
# red blinking - error - usually fatal

def main():

    # initialize all hardware
    # hardware = initializeAllHardware()
    # if None in hardware.values():
    #     print('ERROR: value set to None - this is bad')
    #     closeEverything(hardware)
    #     return None

    # hardware = defineEncoderLimits(hardware, axis='X')
    # hardware = defineEncoderLimits(hardware, axis='Y')

    orange_lower = np.array([10, 140, 140], np.uint8)
    orange_upper = np.array([25, 255, 255], np.uint8)
    cyan_lower = np.array([85, 140, 140], np.uint8)
    cyan_upper = np.array([100, 255, 255], np.uint8)

    board_img = cv2.imread(f'../{imgs[6]}')
    robot_shape_img = cv2.imread(f'../oval_template.png', 0)

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

    while True:
        # wait until button press - ie human turn end and bot turn start
        print('waiting for button to be pressed to start robot turn')
        #hardware['TURN_INDICATOR_BUTTON'].wait_for_press()

        # TODO - click pic and get current board state with piece locations
        # board_img = None
        print(cv_obj.BOARD)

        # update board state
        cv_obj.update_board_state(board_img)

        # check win condition and break loop if win achieved
        print('checking game end condition')
        winner = check_win_condition(cv_obj.BOARD)
        if winner != '':
            print('GAME END')
            print(winner.upper(), 'WON')
            break

        # get next best move
        print('computing next best move')
        next_move_position = tic_tac_toe_logic_v2(cv_obj.BOARD, ROBOT_PIECE)
        print('best move at', next_move_position)

        cv_obj.BOARD[next_move_position] = ROBOT_PIECE

        print(cv_obj.BOARD)
        continue

        # translate position to location
        print('computing real world location of next best move')
        next_move_world_location = translate_position_to_location(next_move_position)

        # can be a safety thing? wait until button released and child has stepped back before motors do things
        if hardware['TURN_INDICATOR_BUTTON'].is_pressed:
            print('waiting for button release if not already done before starting motors')
            hardware['TURN_INDICATOR_BUTTON'].wait_for_release()

        # TODO - get and execute path to accomplish next best move
        print('computing and executing next best move')
        find_and_execute_path(next_move_world_location)

    # closeEverything(hardware)

main()
    





