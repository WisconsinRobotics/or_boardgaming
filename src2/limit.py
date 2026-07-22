import RPi.GPIO as GPIO
import time
from enum import Enum
from constants import *

class LIMIT(Enum):
    X_LIM_NEG = X_LIMIT_SWITCH_NEG_PIN
    X_LIM_POS = X_LIMIT_SWITCH_POS_PIN
    Y_LIM_NEG = Y_LIMIT_SWITCH_NEG_PIN
    Y_LIM_POS = Y_LIMIT_SWITCH_POS_PIN

class LimitManager:
    def __init__(self):
        """Initializes all GPIO pins mapped in the LIMIT Enum."""
        GPIO.setmode(GPIO.BCM)
        for limit in LIMIT:
            GPIO.setup(limit.value, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            print(f"Initialized limit switch {limit.name} on pin {limit.value}")

    @classmethod
    def is_pressed(self, limit: LIMIT) -> bool:
        """Reads the switch state, ensuring activate_limits() was called first."""
        return GPIO.input(limit.value) == GPIO.LOW
