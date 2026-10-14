import time
from gpiozero import Button
from enum import Enum
from constants import *

class LimitManager:
    def __init__(self):
        """Initializes all GPIO pins mapped in the LIMIT Enum."""
        self._map = {}
        self._map[X_LIMIT_SWITCH_NEG_PIN] = Button(X_LIMIT_SWITCH_NEG_PIN, pull_up=True, bounce_time=0.02)
        self._map[Y_LIMIT_SWITCH_NEG_PIN] = Button(Y_LIMIT_SWITCH_NEG_PIN, pull_up=True, bounce_time=0.02)
        print(f"Initialized limit switchs")

    def on_pressed(self, pin: int, callback):
        """registers callback. NOTE: will override prev callback"""
        if pin not in self._map:
            raise ValueError(f"Invalid pin {pin} for registering limit callback")
        self._map[pin].when_pressed = callback
