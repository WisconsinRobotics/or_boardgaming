from dual_max14870_rpi import motors, MAX_SPEED
import Encoder

robot_turn = True
MOTOR_MAX_SPEED = motors.MAX_SPEED
enc = Encoder.Encoder(20, 21) # 5 and 6 are pin numbers

# tracking all previous distances from encoders
prev_loc = 0
# set if robot is using x/o somewhere

### tic tac toe logic ###
# - robot use x, player use o (for now)
# - if middle square is empty, play middle square
# - else tic tac toe algorithm ahagaha
def tic_tac_toe_logic():
    # get board from cv file
    board = [[0,0,0],[0,0,0],[0,0,0]]
    x = 0
    y = 0
    return x

### move robot when it's its turn to move ###
while 1:
    if robot_turn:
        loc_enc = enc.read()
        next_loc = tic_tac_toe_logic()
        motors.enable()
        print(loc_enc)
        # current robot position + updating previous position
        cur_loc = loc_enc - prev_loc

        # distance from desired position
        dist_x = 50 - loc_enc
        dist_y = 0

        x_speed = dist_x * 0.05 # idk some random int
        y_speed = dist_y * 0.05
        print("x speed", x_speed)
        motors.setSpeeds(x_speed, y_speed)
