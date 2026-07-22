from gpiozero import PhaseEnableMotor, RotaryEncoder, Button
from time import sleep
import numpy as np

X_MOTOR_PINS = [12,24]
Y_MOTOR_PINS = [13,25]
MOTOR_SPEED = 0.8
Z_MOTOR_PINS = []

X_ENCODER_PINS = [14,15]
Y_ENCODER_PINS = [7,8]
Z_ENCODER_PINS = []

LIMIT_SWITCH_PIN = None

X_MOTOR = PhaseEnableMotor(X_MOTOR_PINS[0], X_MOTOR_PINS[1])
Y_MOTOR = PhaseEnableMotor(Y_MOTOR_PINS[0], Y_MOTOR_PINS[1])
X_ENCODER = RotaryEncoder(X_ENCODER_PINS[0], X_ENCODER_PINS[1])
Y_ENCODER = RotaryEncoder(Y_ENCODER_PINS[0], Y_ENCODER_PINS[1])

LIMIT_SWITCH = Button(LIMIT_SWITCH_PIN)


def moveMotor(motor, encoder, dist):
    if dist > 0:
        motor.forward(MOTOR_SPEED)
    else:
        motor.backward(MOTOR_SPEED)
    
    sleep(abs(dist))
    motor.stop()

    print('steps:', encoder.steps)
    print('value:', encoder.value)



locs = np.array([[200, 500], [100, 800], [400, 400], [1000, 200]])
for i in range(1, len(locs)):
    loc_diff = locs[i] - locs[i - 1]
    print(loc_diff)
    moveMotor(X_MOTOR, X_ENCODER, loc_diff[0])
    moveMotor(Y_MOTOR, Y_ENCODER, loc_diff[1])
