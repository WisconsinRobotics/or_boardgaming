import numpy as np
import cv2

# Board game settings
ROBOT_PIECE = 'o'
HUMAN_PIECE = 'x'

Y_MOTOR_PWM_PIN = 13
Y_MOTOR_DIR_PIN = 25
X_MOTOR_PWM_PIN = 12
X_MOTOR_DIR_PIN = 24

GEARBOX_CPR = 700
IN_PER_LEAD_REV = .315 # how many inch per rev of lead screw
STEPS_PER_INCH = GEARBOX_CPR / IN_PER_LEAD_REV

# offset for x, y + deadzone
CLAW_X_OFFSET = 4.75 - .5 # from screw sticking out when hitting limit switch -
CLAW_Y_OFFSET = 0.85 # from roller when hitting limit switch -

BOARD_EDGE_OFFSET_FROM_OUTLINE_INCH = 0.75
BOARD_X_OFFSET_INCH = 6.25 + BOARD_EDGE_OFFSET_FROM_OUTLINE_INCH # from screw sticking out when hitting limit switch -
BOARD_Y_OFFSET_INCH = 0 + BOARD_EDGE_OFFSET_FROM_OUTLINE_INCH # from roller when hitting limit switch -

OFFSET_X_INCH = BOARD_X_OFFSET_FROM_LIMIT_SWITCH_INCH + BOARD_EDGE_OFFSET_FROM_OUTLINE_INCH
DEADZONE_STEPS = 0.1 * STEPS_PER_INCH

# CV constants
BOARD_SQUARE_SIZE = [6, 6] # irl size of total board in inches
OUTLINE_LENGTH_INCH = BOARD_SQUARE_SIZE[0]
APPROX_GANTRY_DIMS_IN_CM = 50 # 100 # 19.5 in
ORANGE_LOWER = np.array([10, 140, 140], np.uint8)
ORANGE_UPPER = np.array([25, 255, 255], np.uint8)
GREY_LOWER = np.array([85, 140, 140], np.uint8) # TODO: Change this color to grey
GREY_UPPER = np.array([100, 255, 255], np.uint8)
INITIAL_BOARD_IMG = cv2.imread(f'../{imgs[6]}')
ROBOT_SHAPE_IMG = cv2.imread(f'../oval_template.png', 0)


CLAW_SERVO_PIN = 23 
CLAW_SERVO_MIN = 1/1000
CLAW_SERVO_MAX = 2.2/1000
Z_SERVO_PIN = 18 
Z_SERVO_MIN = 0.7/1000
Z_SERVO_MAX = 2.3/1000

MOTOR_ENABLE_PIN = 5
MOTOR_FAULT_PIN = 6

Y_ENCODER_PINS = [8, 7]
X_ENCODER_PINS = [15, 14]

Y_LIMIT_SWITCH_NEG_PIN = 19 # see physical board, marked as S3
Y_LIMIT_SWITCH_POS_PIN = 26 # marked as S4
X_LIMIT_SWITCH_NEG_PIN = 16 
X_LIMIT_SWITCH_POS_PIN = 20 

TURN_INDICATOR_BUTTON_PIN = 21

REST_LOCATION = [0, 0] # placeholder
PIECE_STORAGE_LOCATION = [0, 0] # placeholder
MOTOR_SPEED = 0.4

COMMAND_FREQUENCY = 20 # 20 hz so 0.05 s
