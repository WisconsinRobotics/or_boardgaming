from gpiozero import PhaseEnableMotor, OutputDevice, RotaryEncoder, Servo, Button
from time import sleep
from constants import *



# Pins based on Pololu MAX14870 Dual Motor Driver for Raspberry Pi
X_MOTOR_PINS = [24, 12]  # Motor A (phase, enable)
Y_MOTOR_PINS = [25, 13]  # Motor B (phase, enable)
SLEEP_PIN = 6             # Shared sleep/enable pin
EN_PIN = 5
MOTOR_SPEED = 0.5
RUN_TIME = 3  # seconds per direction
rotorX= RotaryEncoder(14, 15, wrap=False, max_steps=0) 
rotorY = RotaryEncoder(7,8, wrap=False, max_steps=0)
print("Setting up motors...")

# Initialize sleep (shared enable) pin — active high
SLEEP = OutputDevice(SLEEP_PIN, active_high=True, initial_value=False)

# Initialize motors
X_MOTOR = PhaseEnableMotor(*X_MOTOR_PINS)
Y_MOTOR = PhaseEnableMotor(*Y_MOTOR_PINS)
EN = OutputDevice(EN_PIN, active_high=False, initial_value=True)  # Enable pin needs to be LOW to enable driver
print("Motors setup complete.")


# Wake up the driver
print("Enabling (waking) motor driver...")
SLEEP.on()   # HIGH = active
sleep(0.5)

# Run forward

def runMotorsToPos(targetX, targetY):
    print("Target X :", targetX, " Target Y :", targetY)
    X_MOTOR.forward(MOTOR_SPEED)
    Y_MOTOR.forward(MOTOR_SPEED)
    while rotorX.steps < targetX or rotorY.steps < targetY:
        if (rotorX.steps >= targetX):
            X_MOTOR.stop()
        if (rotorY.steps >= targetY):
            Y_MOTOR.stop()

    X_MOTOR.stop()
    Y_MOTOR.stop()
    X_MOTOR.backward(0.1)
    sleep(0.001)
    while (rotorX.steps > targetX):
        pass
    
        
    X_MOTOR.stop()
    sleep(0.1)
    #print("Final StepsX ", rotorX.steps - 10)
    Y_MOTOR.backward(0.2)
    while (rotorY.steps > targetY):
        pass
    Y_MOTOR.stop()
    X_MOTOR.stop()
    Y_MOTOR.stop()


    print("Final StepsX ", rotorX.steps)
    print("Final StepsY ", rotorY.steps)
runMotorsToPos(1200, 400)