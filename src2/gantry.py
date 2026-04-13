# To run this file, make sure to run sudo pigpiod beforehand

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
        self.is_x_homed = False
        self.is_y_homed = False

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
 
    # expect speed to be between -1.0 and 1.0
    def set_x_vel(self, speed: float):
        if speed < -1 or speed > 1:
            raise ValueError("speed should be between -1.0 and 1.0 ", speed)

        if speed > 0:
            self.X_MOTOR.backward(speed)
        elif speed < 0:
            self.X_MOTOR.forward(-speed)
        else:
            self.X_MOTOR.stop()

    def set_y_vel(self, speed: float):
        if speed < -1 or speed > 1:
            raise ValueError("speed should be between -1.0 and 1.0 ", speed)

        # direction is intentionally inverted - if motor changes double check this is correct
        if speed > 0:
            self.Y_MOTOR.forward(speed)
        elif speed < 0:
            self.Y_MOTOR.backward(-speed)
        else:
            self.Y_MOTOR.stop()

    def home_y(self, speed=0.3):
        self.set_y_vel(-speed)
        while not self._is_pressed(LIMIT.Y_LIM_NEG):
            print("encoder: ", self.Y_ENCODER.steps)
            time.sleep(0.01)
        self.Y_MOTOR.stop()
        self.Y_ENCODER.value = 0
        self.is_homed = True

        self.set_y_val(speed)
        start_time = time.time()
        # keep spinning for 5 seconds
        while (time.time() - start_time) < 5:
            print(self.Y_ENCODER.steps)
            time.sleep(0.1)
        self.Y_MOTOR.stop()
        self.is_y_homed = True

    def home_x(self, speed=0.3):
        self.set_x_vel(-speed)
        while not self._is_pressed(LIMIT.X_LIM_NEG):
            print("encoder: ", self.X_ENCODER.steps)
            time.sleep(0.01)
        self.X_MOTOR.stop()
        self.X_ENCODER.value = 0
        self.is_homed = True

        self.set_x_val(speed)
        start_time = time.time()
        # keep spinning for 5 seconds
        while (time.time() - start_time) < 5:
            print(self.X_ENCODER.steps)
            time.sleep(0.1)
        self.X_MOTOR.stop()
        self.is_x_homed = True

    def get_x_pos_inches(self):
        return self.X_ENCODER.steps / STEPS_PER_INCH

    def get_y_pos_inches(self):
        """Returns current position in inches based on encoder steps."""
        return self.Y_ENCODER.steps / STEPS_PER_INCH

    def move(self, x: float, y: float):
        if not self.is_x_homed:
            raise ValueError("Need to call home_x() before moving")
        elif not self.is_y_homed:
            raise ValueError("Need to call home_y() before moving")
          
    def _move_smoothly(self, servo, start_val, end_val, steps=20, duration=0.5):
        """Moves a servo from start_val to end_val over a set duration."""
        delay = duration / steps
        for i in range(steps + 1):
            # Linear interpolation between start and end
            fraction = i / steps
            current_pos = start_val + (end_val - start_val) * fraction
            servo.value = current_pos
            time.sleep(delay)

    def toggle_grab(self):
        self.is_grabbing = not self.is_grabbing
        
        # Speed settings (adjust these to your liking)
        # Lower duration = faster movement
        Z_SPEED = 0.8  
        CLAW_SPEED = 0.6 

        if self.is_grabbing:
            # 1. Raise Z-Servo (Min to Max)
            self._move_smoothly(self.Z_SERVO, -1.0, 1.0, duration=Z_SPEED)
            # 2. Close Claw (Max to Min)
            self._move_smoothly(self.CLAW_SERVO, 1.0, -1.0, duration=CLAW_SPEED)
            time.sleep(0.5)
            # 3. Lower Z-Servo (Max to Min)
            self._move_smoothly(self.Z_SERVO, 1.0, -1.0, duration=Z_SPEED)
        else:
            # 1. Raise Z-Servo (Min to Max)
            self._move_smoothly(self.Z_SERVO, -1.0, 1.0, duration=Z_SPEED)
            # 2. Open Claw (Min to Max)
            self._move_smoothly(self.CLAW_SERVO, -1.0, 1.0, duration=CLAW_SPEED)
            time.sleep(0.5)
            # 3. Lower Z-Servo (Max to Min)
            self._move_smoothly(self.Z_SERVO, 1.0, -1.0, duration=Z_SPEED)

