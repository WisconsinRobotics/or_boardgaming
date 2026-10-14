# To run this file, make sure to run sudo pigpiod beforehand
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
from dual_max_motor.dual_max14870_rpi import motors, MAX_SPEED

from gpiozero import OutputDevice, RotaryEncoder, DigitalInputDevice
from constants import *
from limit import *
import time

class Gantry():
    def __init__(self):
        self.is_x_homed = False
        self.is_y_homed = False

        self.limit = LimitManager()

        print('Starting motor setup')

        time.sleep(0.5)
        self.Y_MOTOR = motors.motor2
        self.X_MOTOR = motors.motor1
        motors.enable()
        print('Motors successfully setup')

        print('Starting encoder setup')
        # B before A for direction alignment
        self.X_ENCODER = RotaryEncoder(X_ENCODER_B, X_ENCODER_A, max_steps = 0)
        self.Y_ENCODER = RotaryEncoder(Y_ENCODER_B, Y_ENCODER_A, max_steps = 0)
        print('Encoders successfully setup')
          
    def __del__(self):
        motors.setSpeeds(0, 0)
        motors.disable()

    def home_y(self, speed=0.3):

        def on_limit_reached():
            print("================= y limit reached ====================")
            self.Y_MOTOR.setSpeed(0)
            self.Y_ENCODER.value = 0
            self.Y_MOTOR.forward(MAX_SPEED / 4)
            start_time = time.time()
            # keep spinning for 3 seconds
            time.sleep(3)
            self.Y_MOTOR.setSpeed(0)
            self.is_y_homed = True

        self.limit.on_pressed(Y_LIMIT_SWITCH_NEG_PIN, on_limit_reached)
        print("Callback registered for Y limit switch")
        self.Y_MOTOR.setSpeed(-MAX_SPEED / 4)
        print("Y motor moving backward to home position")
        
        while not self.is_y_homed:
            print("encoder: ", self.Y_ENCODER.steps)
            #print("fault pin: ", self.MOTOR_FAULT.is_active)
            #print(f"en pin: {self.EN.is_active}" )
            time.sleep(0.25)

        
    def home_x(self, speed=0.3):
        def on_limit_reached():
            print("================== x limit reached ====================")
            self.X_MOTOR.setSpeed(0)
            self.X_ENCODER.value = 0
            self.X_MOTOR.setSpeed(MAX_SPEED / 4)
            start_time = time.time()
            time.sleep(3)
            self.X_MOTOR.setSpeed(0)
            self.is_x_homed = True

        self.limit.on_pressed(X_LIMIT_SWITCH_NEG_PIN, on_limit_reached)
        self.X_MOTOR.setSpeed(MAX_SPEED / 4)

        while not self.is_x_homed:
            print("encoder: ", self.X_ENCODER.steps)
            #print("fault pin: ", self.MOTOR_FAULT.is_active)
            #print(f"en pin: {self.EN.is_active}" )
            time.sleep(1)

       
    def get_x_pos_inches(self):
        return self.X_ENCODER.steps / STEPS_PER_INCH

    def get_y_pos_inches(self):
        """Returns current position in inches based on encoder steps."""
        return self.Y_ENCODER.steps / STEPS_PER_INCH

    def move_to_coordinate(self, target_x_inch, target_y_inch, speed=0.8):
        """
        Moves the gantry to a specific (X, Y) coordinate using encoder feedback.
        Assumes units like millimeters or inches based on your STEPS_PER_UNIT configuration.
        """
        # 1. Convert physical coordinates into raw target encoder steps
        target_x_steps = int(target_x_inch * STEPS_PER_INCH)
        target_y_steps = int(target_y_inch * STEPS_PER_INCH)
        
        print(f"Moving to ({target_x_inch} in, {target_y_inch} in) -> Target Steps: X={target_x_steps}, Y={target_y_steps}")

        while True:
            # 2. Read current real-time encoder positions
            current_x = self.X_ENCODER.steps
            current_y = self.Y_ENCODER.steps
            
            # 3. Calculate distance remaining
            error_x = target_x_steps - current_x
            error_y = target_y_steps - current_y
            #print(f"error_x={error_x / STEPS_PER_INCH}, error_y={error_y / STEPS_PER_INCH}")
            
            # Check if BOTH axes have arrived within the allowed deadzone
            if abs(error_x) <= DEADZONE_STEPS and abs(error_y) <= DEADZONE_STEPS:
                break
                
            # 4. Handle X-Axis Navigation
            if abs(error_x) > DEADZONE_STEPS:
                if error_x > 0:
                    self.X_MOTOR.forward(speed)
                else:
                    self.X_MOTOR.backward(speed)
            else:
                self.X_MOTOR.stop()

            # 5. Handle Y-Axis Navigation
            if abs(error_y) > DEADZONE_STEPS:
                if error_y > 0:
                    self.Y_MOTOR.forward(speed)
                else:
                    self.Y_MOTOR.backward(speed)
            else:
                self.Y_MOTOR.stop()
                
            # Tiny sleep to keep the CPU from redlining during the while loop
            time.sleep(0.01)

        # 6. Safety Stop once destination is successfully reached
        self.X_MOTOR.stop()
        self.Y_MOTOR.stop()
        print(f"Arrival confirmed at actual position: X={self.X_ENCODER.steps}, Y={self.Y_ENCODER.steps}")
        self.EN.off()

    def move_to_board_cell(self, row, col):
        target_x = BOARD_X_OFFSET + row * BOARD_SQUARE_SIZE[0]/3 + BOARD_SQUARE_SIZE[0]/6 - CLAW_X_OFFSET
        target_y = BOARD_Y_OFFSET + col * BOARD_SQUARE_SIZE[1]/3 + BOARD_SQUARE_SIZE[1]/6 - CLAW_Y_OFFSET
        self.move_to_coordinate(target_x, target_y)
        
    def move_to_pickup_piece(self):
        target_x = BOARD_X_OFFSET - 2.5 - CLAW_X_OFFSET
        target_y = BOARD_Y_OFFSET + 2 - CLAW_Y_OFFSET
        print("pick up loc: ", target_x, ", ", target_y)
        self.move_to_coordinate(target_x, target_y)

