import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
from dual_max_motor.dual_max14870_rpi import motors, MAX_SPEED
from gpiozero import RotaryEncoder
from constants import *
from watchdog import WatchdogClient
import time

# B before A for direction alignment
ENCODER = RotaryEncoder(Y_ENCODER_B, Y_ENCODER_A, max_steps=0)
# Initialize using the built-in PhaseEnableMotor class

try:
    client = WatchdogClient()
    motors.setSpeeds(0, 0)
    print("Starting motor test with dual_max...")

    # 1. Move forward at 10% speed
    print("Moving forward (10% speed)...")
    motors.motor2.setSpeed(MAX_SPEED / 3)

    start_time = time.time()
    # keep spinning for 1 second
    while (time.time() - start_time) < 1:
        print(ENCODER.steps / STEPS_PER_INCH)
        client.send_heartbeat()
        time.sleep(0.05)

    # 3. Move backward at 10% speed
    print("Moving backward (10% speed)...")
    motors.motor2.setSpeed(-MAX_SPEED / 3)

    start_time = time.time()
    # keep spinning for 1 second
    while (time.time() - start_time) < 1:
        print(ENCODER.steps / STEPS_PER_INCH)
        client.send_heartbeat()
        time.sleep(0.05)


finally:
    # Safely stop and release pins on exit
    print("Stopping motor and cleaning up.")
    motors.setSpeeds(0, 0)
