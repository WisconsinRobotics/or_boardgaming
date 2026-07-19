import cv2
from gpiozero import PhaseEnableMotor, OutputDevice, RotaryEncoder, Servo, Button
from constants import *
import os
import threading



def initCamera(res):
    print(f'Starting Camera Task assigned to thread: {threading.current_thread().name}')
    print(f'ID of process running task 1: {os.getpid()}')

    res['CAMERA'] = cv2.VideoCapture(0)
    if not res['CAMERA'].isOpened():
        res['CAMERA'] = None
        print('ERROR: Cannot open camera')
    return res


    print('Camera successfully started')

def initializeAllHardware():
    res = {}


    t1 = threading.Thread(target=initCamera, args=(res))

    
    # print('Starting Camera')
    # res['CAMERA'] = cv2.VideoCapture(0)
    # if not res['CAMERA'].isOpened():
    #     res['CAMERA'] = None
    #     print('ERROR: Cannot open camera')
    #     return res

    # print('Camera successfully started')

    print('Starting motor setup')
    res['X_MOTOR'] = PhaseEnableMotor(*X_MOTOR_PINS)
    res['Y_MOTOR'] = PhaseEnableMotor(*Y_MOTOR_PINS)
    # res['Z_MOTOR'] = PhaseEnableMotor(**Z_MOTOR_PINS)

    X_MOTOR_ENABLE = OutputDevice(X_MOTOR_ENABLE_PIN, active_high=False, initial_value=True)
    Y_MOTOR_ENABLE = OutputDevice(Y_MOTOR_ENABLE_PIN, active_high=False, initial_value=True)
    # Z_MOTOR_ENABLE = OutputDevice(Z_MOTOR_ENABLE_PIN, active_high=False, initial_value=True)
    print('Motors successfully setup')
    
    print('Starting encoder setup')
    res['X_ENCODER'] = RotaryEncoder(**X_ENCODER_PINS, max_steps=0)
    printf("x encoder pin = ", X_ENCODER_PINS)
    res['Y_ENCODER'] = RotaryEncoder(**Y_ENCODER_PINS, max_steps=0)
    printf("y encoder pin = ", Y_ENCODER_PINS)
    # res['Z_ENCODER'] = RotaryEncoder(**Z_ENCODER_PINS, max_steps=0)
    print('Encoders successfully setup')

    print('Starting servo setup')
    res['CLAW_SERVO'] = Servo(CLAW_SERVO_PIN)
    res['Z_SERVO'] = Servo(Z_SERVO_PIN)
    print('Servo successfully setup')

    print('Starting button setup (limit switches and main button)')

    res['X_FWD_SWITCH'] = Button(X_FORWARD_LIMIT_SWITCH_PIN, pull_up=False)
    res['X_BKD_SWITCH'] = Button(X_BACKWARD_LIMIT_SWITCH_PIN, pull_up=False)
    res['Y_FWD_SWITCH'] = Button(Y_FORWARD_LIMIT_SWITCH_PIN, pull_up=False)
    res['Y_BKD_SWITCH'] = Button(Y_BACKWARD_LIMIT_SWITCH_PIN, pull_up=False)
    # res['TURN_INDICATOR_BUTTON'] = Button(TURN_INDICATOR_BUTTON_PIN, pull_up=False)

    print('Buttons successfully setup')

    return res


def mechanicalCheck(hardware):
    # basically a function to yell at mechanical for non software issues

    return True

def defineEncoderLimits(hardware, axis):
    print('defining encoder limits')
    motor, encoder, forward_switch, backward_switch = (
        hardware[f'{axis}_MOTOR'],
        hardware[f'{axis}_ENC'],
        hardware[f'{axis}_FWD_SWITCH'],
        hardware[f'{axis}_BKD_SWITCH']
    )

    if forward_switch.is_pressed:
        motor.backward(MOTOR_SPEED)
        forward_switch.wait_for_release()
        motor.stop()

    motor.forward(MOTOR_SPEED)
    forward_switch.wait_for_press()
    motor.stop()
    forward_lim = encoder.steps

    motor.backward(MOTOR_SPEED)
    backward_switch.wait_for_press()
    motor.stop()
    backward_lim = encoder.steps

    print('encoder limits defined as:', forward_lim, backward_lim)

    hardware[f'{axis}_FWD_LIM'] = forward_lim
    hardware[f'{axis}_BKD_LIM'] = backward_lim
    return hardware

def closeEverything(hardware):
    if not (hardware['CAMERA'] is None) and hardware['CAMERA'].isOpened():
        hardware['CAMERA'].release()

    cv2.destroyAllWindows()
