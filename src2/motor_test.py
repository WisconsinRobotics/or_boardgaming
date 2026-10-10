from gpiozero import PhaseEnableMotor, OutputDevice, RotaryEncoder
from constants import *
import time

# --- Pin Configuration (Change these to match your wiring) ---
PHASE_PIN = X_MOTOR_DIR_PIN # Controls direction
ENABLE_PIN = X_MOTOR_PWM_PIN # Controls speed (PWM)

# B before A for direction alignment
ENCODER = RotaryEncoder(X_ENCODER_B, X_ENCODER_A, max_steps=0)
# Initialize using the built-in PhaseEnableMotor class
motor = PhaseEnableMotor(phase=PHASE_PIN, enable=ENABLE_PIN)
MOTOR_ENABLE = OutputDevice(MOTOR_ENABLE_PIN, active_high=False, initial_value=False)

try:
    MOTOR_ENABLE.on()
    print("Starting motor test with PhaseEnableMotor...")

    # 1. Move forward at 10% speed
    print("Moving forward (10% speed)...")
    motor.forward(speed=0.3)

    start_time = time.time()
    # keep spinning for 1 second
    while (time.time() - start_time) < 1:
        print(ENCODER.steps / STEPS_PER_INCH)
        time.sleep(0.05)

    # 2. Stop
    print("Stopping...")
    motor.stop()

    time.sleep(1)

    # 3. Move backward at 10% speed
    print("Moving backward (10% speed)...")
    motor.backward(speed=0.3)

    start_time = time.time()
    # keep spinning for 1 second
    while (time.time() - start_time) < 1:
        print(ENCODER.steps / STEPS_PER_INCH)
        time.sleep(0.05)


finally:
    # Safely stop and release pins on exit
    print("Stopping motor and cleaning up.")
    motor.stop()