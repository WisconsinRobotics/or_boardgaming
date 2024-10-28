from dual_max14870_rpi import motors, MAX_SPEED
import encoders

robot_turn = False
MOTOR_MAX_SPEED = motors.MAX_SPEED

# tracking all previous distances from encoders
prev_x = 0
prev_y = 0
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

### move robot when it's its turn to move ###
if robot_turn:
    [x_enc, y_enc] = encoders.readEncoders() # current location
    [next_x, next_y] = tic_tac_toe_logic()
    motors.enable()

    # current robot position + updating previous position
    cur_x = x_enc - prev_x
    cur_y = y_enc - prev_y
    prev_x = x_enc
    prev_y = x_enc

    # distance from desired position
    dist_x = next_x - cur_x
    dist_y = next_y - cur_y

    x_speed = dist_x * 5 # idk some random int
    y_speed = dist_y * 5
    motors.setSpeeds(x_speed, y_speed)