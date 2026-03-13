from enum import Enum
from gpiozero import PhaseEnableMotor, OutputDevice, RotaryEncoder, Servo, Button, Device
import RPi.GPIO as GPIO
from constants import *
import time
from gpiozero.pins.pigpio import PiGPIOFactory

Device.pin_factory = PiGPIOFactory()
class LIMIT(Enum):
    X_LIM_NEG = 0
    X_LIM_POS = 1
    Y_LIM_NEG = 2 
    Y_LIM_POS = 3 

class Gantry():
    def __init__(self):
        self.is_homed = False

        print('Starting motor setup')
        self.X_MOTOR = PhaseEnableMotor(*X_MOTOR_PINS)
        self.Y_MOTOR = PhaseEnableMotor(*Y_MOTOR_PINS)

        self.X_MOTOR_ENABLE = OutputDevice(X_MOTOR_ENABLE_PIN, active_high=False, initial_value=True)
        self.Y_MOTOR_ENABLE = OutputDevice(Y_MOTOR_ENABLE_PIN, active_high=False, initial_value=True)
        print('Motors successfully setup')

        print('Starting encoder setup')
        self.X_ENCODER = RotaryEncoder(*X_ENCODER_PINS, max_steps=0)
        self.Y_ENCODER = RotaryEncoder(*Y_ENCODER_PINS, max_steps=0)
        print('Encoders successfully setup')

        print('Starting limit switch setup')
        GPIO.setmode(GPIO.BCM)
        self.Y_LIMIT_SWITCH_NEG_PIN = Y_LIMIT_SWITCH_NEG_PIN
        GPIO.setup(Y_LIMIT_SWITCH_NEG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.Y_LIMIT_SWITCH_POS_PIN = Y_LIMIT_SWITCH_POS_PIN
        GPIO.setup(Y_LIMIT_SWITCH_POS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print('Limit switches successfully setup')

        print('Starting servo setup')
        self.CLAW_SERVO = Servo(CLAW_SERVO_PIN)
        self.Z_SERVO = Servo(Z_SERVO_PIN, min_pulse_width=Z_SERVO_MIN, max_pulse_width=Z_SERVO_MAX)
        print('Servo successfully setup')
        self.Z_SERVO.min()
        self.CLAW_SERVO.max()
        self.is_grabbing = False

    def _is_pressed(self, limit: LIMIT):
        if (limit == LIMIT.X_LIM_NEG):
            return GPIO.input(X_LIMIT_SWITCH_NEG_PIN) == GPIO.LOW
        elif (limit == LIMIT.X_LIM_POS):
            return GPIO.input(X_LIMIT_SWITCH_POS_PIN) == GPIO.LOW
        elif (limit == LIMIT.Y_LIM_NEG):
            return GPIO.input(self.Y_LIMIT_SWITCH_NEG_PIN) == GPIO.LOW
        elif (limit == LIMIT.Y_LIM_POS):
            return GPIO.input(self.Y_LIMIT_SWITCH_POS_PIN) == GPIO.LOW
        else:
            raise ValueError("unexpected arg for is_pressed: " + limit)

    def home(self, speed=0.3):
        self.Y_MOTOR.backward(speed)
        while not self._is_pressed(LIMIT.Y_LIM_NEG):
            print("encoder: ", self.Y_ENCODER.steps)
            time.sleep(0.01)
        self.Y_MOTOR.stop()
        self.Y_ENCODER.value = 0
        self.is_homed = True

        self.Y_MOTOR.forward(speed)
        start_time = time.time()
        while (time.time() - start_time) < 5:
            print(self.Y_ENCODER.steps)
            time.sleep(0.1)
        self.Y_MOTOR.stop()

    def get_pos_inches(self):
        """Returns current position in inches based on encoder steps."""
        return self.Y_ENCODER.steps / STEPS_PER_INCH

    def move(self, x: float, y: float):
        if not self.is_homed:
            raise ValueError("Need to call home() before moving")
    
    def move_x(self, x: float):
        if x > 750:
            self.X_MOTOR.forward(0.3)
        elif x < 250:
            self.X_MOTOR.backward(0.3)
        else:
            self.X_MOTOR.stop()

    def move_y(self, y: float):
        if y > 750:
            self.Y_MOTOR.forward(0.3)
        elif y < 250:
            self.Y_MOTOR.backward(0.3)
        else:
            self.Y_MOTOR.stop()
        
    def toggle_grab(self):
        self.is_grabbing = not self.is_grabbing
        if (self.is_grabbing):
            self.Z_SERVO.max()
            self.CLAW_SERVO.min()
            time.sleep(1)
            self.Z_SERVO.min()
        else:
            self.Z_SERVO.max()
            self.CLAW_SERVO.max()
            time.sleep(1)
            self.Z_SERVO.min()
