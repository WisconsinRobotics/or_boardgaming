import cv2
from gpiozero import PhaseEnableMotor, OutputDevice, RotaryEncoder, Servo, Button
from constants import *

def initializeAllHardware():
    res = {}
    
    print('Starting Camera')
    res['CAMERA'] = cv2.VideoCapture(0)
    if not res['CAMERA'].isOpened():
        res['CAMERA'] = None
        print('Cannot open camera')
        return res

    print('Camera successfully started')

    print('Starting motor setup')
    res['X_MOTOR'] = PhaseEnableMotor(**X_MOTOR_PINS)
    res['Y_MOTOR'] = PhaseEnableMotor(**Y_MOTOR_PINS)
    # res['Z_MOTOR'] = PhaseEnableMotor(**Z_MOTOR_PINS)

    X_MOTOR_ENABLE = OutputDevice(X_MOTOR_ENABLE_PIN, active_high=False, initial_value=True)
    Y_MOTOR_ENABLE = OutputDevice(Y_MOTOR_ENABLE_PIN, active_high=False, initial_value=True)
    # Z_MOTOR_ENABLE = OutputDevice(Z_MOTOR_ENABLE_PIN, active_high=False, initial_value=True)
    print('Motors successfully setup')
    
    print('Starting encoder setup')
    res['X_ENCODER'] = RotaryEncoder(**X_ENCODER_PINS, max_steps=0)
    res['Y_ENCODER'] = RotaryEncoder(**Y_ENCODER_PINS, max_steps=0)
    # res['Z_ENCODER'] = RotaryEncoder(**Z_ENCODER_PINS, max_steps=0)
    print('Encoders successfully setup')

    # print('Starting servo setup')
    # res['CLAW_SERVO'] = Servo(CLAW_SERVO_PIN)
    # print('Servo successfully setup')

    # print('Starting button setup (limit switches and main button)')
    # res['X_LIMIT_SWITCH'] = Button(X_LIMIT_SWITCH_PIN)
    # res['Y_LIMIT_SWITCH'] = Button(Y_LIMIT_SWITCH_PIN)
    # res['TURN_INDICATOR_BUTTON'] = Button(TURN_INDICATOR_BUTTON_PIN)
    # print('Buttons successfully setup')

    return res

def closeEverything(hardware):
    if not (hardware['CAMERA'] is None) and hardware['CAMERA'].isOpened():
        hardware['CAMERA'].release()

    cv2.destroyAllWindows()