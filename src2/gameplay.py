SAMPLE_TEST = True

import cv2, os, time
import numpy as np
from tic_tac_toe_logic_v2 import tic_tac_toe_logic_v2, check_win_condition
from path_planning import find_and_execute_path
if not SAMPLE_TEST:
    from hardware_setup import *
from cv_functions import *
from camera import *
from gantry import *


imgs = list(filter(lambda x: x.endswith('jpg'), os.listdir('..')))

# colors:
# blue blinking - bot turn start - computing best move n waypoints
# yellow blinking - actual moving - humans beware
# green solid - bot turn end - human move
# red blinking - error - usually fatal



def main():
    if not SAMPLE_TEST:
        # initialize all hardware
        camera = Camera()
        gantry = Gantry()

    board_img = cv2.imread(f'../{imgs[6]}')
    robot_shape_img = cv2.imread(f'../oval_template.png', 0)

    cv_obj = Generic_Board_Game_CV(
            board_dims = (3, 3),
            initial_image = INITIAL_BOARD_IMG,
            piece_diff_method = 'color',
            piece_values = {
                'robot': {
                    'label': 'o',
                    'color_values': [ORANGE_LOWER, ORANGE_UPPER],
                    'shape_values': generate_shape_template('oval', shape_img = ROBOT_SHAPE_IMG)
                },
                'human': {
                    'label': 'x',
                    'color_values': [GREY_LOWER, GREY_UPPER],
                    'shape_values': generate_shape_template('cross')
                }
            },
            debug = False
        )
    

    i = 0
    while True:
        if i > 10:
            break
        print(cv_obj.BOARD)

        # wait until button press - ie human turn end and bot turn start
        print('\nwaiting for button to be pressed to start robot turn')
        input("Press Enter for robot's turn")
        #hardware['TURN_INDICATOR_BUTTON'].wait_for_press()

        # TODO - click pic and get current board state with piece locations
        board_img = camera.clickPicture()

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

        i += 1
        if SAMPLE_TEST:
            continue
        # translate position to location
        #print('computing real world location of next best move')
        #next_move_world_location = translate_position_to_location(next_move_position)

        # can be a safety thing? wait until button released and child has stepped back before motors do things
        #if hardware['TURN_INDICATOR_BUTTON'].is_pressed:
        #    print('waiting for button release if not already done before starting motors')
        #    hardware['TURN_INDICATOR_BUTTON'].wait_for_release()

        # TODO - get and execute path to accomplish next best move
        print('computing and executing next best move')
        gantry.move_to_cell(next_move_position[0], next_move_position[1])
        #find_and_execute_path(next_move_world_location)

    # closeEverything(hardware)

main()
    





