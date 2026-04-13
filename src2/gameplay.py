import cv2, os, time
import numpy as np
from tic_tac_toe_logic_v2 import tic_tac_toe_logic_v2, check_win_condition
from path_planning import find_and_execute_path
from hardware_setup import *
from cv_functions import *





def main():

    # initialize all hardware
    hardware = initializeAllHardware()
    if None in hardware.values():
        print('ERROR: value set to None - this is bad')
        closeEverything(hardware)
        return None

    hardware = defineEncoderLimits(hardware, axis='X')
    hardware = defineEncoderLimits(hardware, axis='Y')

    Tic_Tac_Toe_CV(robot_piece='x')


    while True:
        # wait until button press - ie human turn end and bot turn start
        print('waiting for button to be pressed to start robot turn')
        #hardware['TURN_INDICATOR_BUTTON'].wait_for_press()

        # TODO - click pic and get current board state with piece locations
        # TODO - translate piece locations to piece positions and return board with all piece positions

        # check win condition and break loop if win achieved
        print('checking game end condition')
        winner = check_win_condition(BOARD)
        if winner != '':
            print('GAME END')
            print(winner.upper(), 'WON')
            break

        # get next best move
        print('computing next best move')
        next_move_position = tic_tac_toe_logic_v2(BOARD, ROBOT_PIECE)

        BOARD[next_move_position] = ROBOT_PIECE

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

    closeEverything(hardware)


    




# colors:
# blue blinking - bot turn start - computing best move n waypoints
# yellow blinking - actual moving - humans beware
# green solid - bot turn end - human move
# red blinking - error - usually fatal
