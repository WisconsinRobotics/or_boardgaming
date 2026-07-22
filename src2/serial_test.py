import serial
import time
from gantry import *
import re

PORT = "/dev/ttyUSB0"   # change to /dev/ttyUSB0 if needed
BAUD = 115200

arduino = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)
gantry = Gantry()

def read_joystick():
    
    line = arduino.read_all().decode("utf-8", errors="ignore").strip()
    if not line:
        return None
    pattern = r"Button Pressed:\s+(\d+)\s+Rx value:\s+(\d+)\s+Ry value:\s+(\d+)" 
    button, y, x = re.findall(pattern, line)[-1] 
    return int(x), int(y), int(button)

while True:
    data = read_joystick()
    last_button = 1
    if data is not None:
        x, y, button = data
        print(f"X={x} Y={y} BUTTON={button}")
        gantry.move_y(y)
        gantry.move_x(x)
        if last_button != button:
            last_button = button
            gantry.toggle_grab()

    time.sleep(0.05)
