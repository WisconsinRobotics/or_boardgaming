from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from constants import *
import time

# Speed settings (adjust these to your liking)
# Lower duration = faster movement
Z_SPEED = 0.8  
CLAW_SPEED = 0.6 

class Claw():
    def __init__(self):
        print('Starting servo setup')
        self.CLAW_SERVO = Servo(CLAW_SERVO_PIN, min_pulse_width=CLAW_SERVO_MIN, max_pulse_width=CLAW_SERVO_MAX, pin_factory=PiGPIOFactory())
        self.Z_SERVO = Servo(Z_SERVO_PIN, min_pulse_width=Z_SERVO_MIN, max_pulse_width=Z_SERVO_MAX, pin_factory=PiGPIOFactory())
        print('Servo successfully setup')
        self._move_smoothly(self.Z_SERVO, self.Z_SERVO.value, -1)
        self._move_smoothly(self.CLAW_SERVO, self.CLAW_SERVO.value, -1)
        time.sleep(3)
        print('Claw ready')

    def _move_smoothly(self, servo, start_val, end_val, steps=20, duration=0.5):
        """Moves a servo from start_val to end_val over a set duration."""
        delay = duration / steps
        for i in range(steps + 1):
            # Linear interpolation between start and end
            fraction = i / steps
            current_pos = start_val + (end_val - start_val) * fraction
            servo.value = current_pos
            time.sleep(delay)

    def drop_piece(self):
        # 1. Raise Z-Servo (Min to Max)
        self._move_smoothly(self.Z_SERVO, -1.0, 1.0, duration=Z_SPEED)
        # 2. Open Claw (Min to Max)
        self._move_smoothly(self.CLAW_SERVO, 1.0, -1.0, duration=CLAW_SPEED)
        time.sleep(0.5)
        # 3. Lower Z-Servo (Max to Min)
        self._move_smoothly(self.Z_SERVO, 1.0, -1.0, duration=Z_SPEED)

    def pick_piece(self):
        # 1. Raise Z-Servo (Min to Max)
        self._move_smoothly(self.Z_SERVO, -1.0, 1.0, duration=Z_SPEED)
        # 2. Close Claw (Max to Min)
        self._move_smoothly(self.CLAW_SERVO, -1.0, 0.94, duration=CLAW_SPEED)
        time.sleep(0.5)
        # 3. Lower Z-Servo (Max to Min)
        self._move_smoothly(self.Z_SERVO, 1.0, -1.0, duration=Z_SPEED)
