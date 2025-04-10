import cv2
import numpy as np
import os, time
from corner_detection import determineBoardCorners
from color_detection import detectBoardPieceLocations
#from tic_tac_toe_logic import tic_tac_toe_logic
from tic_tac_toe_logic_v2 import tic_tac_toe_logic_v2, check_win_condition
from path_planning import translate_position_to_location, find_and_execute_path
from gpiozero import PhaseEnableMotor

X_MOTOR_PINS = [12,24]
Y_MOTOR_PINS = [13,25]
Z_MOTOR_PINS = []

X_ENCODER = [14,15]
Y_ENCODER = [7,8]
Z_ENCODER = []

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
            os.makedirs('../images/', exist_ok = True)
            cv2.imwrite(f'../images/img_{count}_{int(time.time())}.png', frame)
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
# yellow blinking - actual moving - humans beware
# green solid - bot turn end - human move
# red blinking - error - usually fatal

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        errorHandle('Cannot open camera')
    board = boardSetup()
    bot_piece = 'x'

    X_MOTOR = PhaseEnableMotor(X_MOTOR_PINS[0],X_MOTOR_PINS[1])
    Y_MOTOR = PhaseEnableMotor(Y_MOTOR_PINS[0],Y_MOTOR_PINS[1])

    while True:
        # click pic and get current board state with piece locations
        # translate piece locations to piece positions and return board with all piece positions

        # check win condition and break loop if win achieved
        winner = check_win_condition(board)
        if winner != '':
            print('GAME END')
            print(winner.upper(), 'WON')
            break
        # get next best move
        next_move_position = tic_tac_toe_logic_v2(board, bot_piece)
        # translate position to location
        new_location = translate_position_to_location(next_move_position)
        # get and execute path to accomplish next best move
        find_and_execute_path(new_location)
        # wait until button press - ie human turn end and bot turn start

    cap.release()
    cv2.destroyAllWindows()

    
