# To run this file, make sure to run sudo pigpiod beforehand

from gpiozero import PhaseEnableMotor, OutputDevice, RotaryEncoder, DigitalInputDevice
from constants import *
from limit import *
import time

class Gantry():
    def __init__(self):
        self.is_x_homed = False
        self.is_y_homed = False

        self.limit = LimitManager()

        print('Starting motor setup')

        self.EN = OutputDevice(MOTOR_ENABLE_PIN, active_high=False, initial_value=False)
        time.sleep(0.5)
        self.MOTOR_FAULT = DigitalInputDevice(MOTOR_FAULT_PIN, pull_up=True)
        self.X_MOTOR = PhaseEnableMotor(X_MOTOR_DIR_PIN, X_MOTOR_PWM_PIN)
        self.Y_MOTOR = PhaseEnableMotor(Y_MOTOR_DIR_PIN, Y_MOTOR_PWM_PIN)

        time.sleep(0.1)
        print('Motors successfully setup')

        print('Starting encoder setup')
        self.X_ENCODER = RotaryEncoder(*X_ENCODER_PINS, max_steps=0)
        self.Y_ENCODER = RotaryEncoder(*Y_ENCODER_PINS, max_steps=0)
        print('Encoders successfully setup')
      
    def home_y(self, speed=0.3):
        self.EN.on()
        self.Y_MOTOR.backward(speed)
        while not self.limit.is_pressed(LIMIT.Y_LIM_NEG):
            print("encoder: ", self.Y_ENCODER.steps)
            print("fault pin: ", self.MOTOR_FAULT.is_active)
            print(f"en pin: {self.EN.is_active}" )
            time.sleep(0.01)
        self.Y_MOTOR.stop()
        self.Y_ENCODER.value = 0

        self.Y_MOTOR.forward(speed)
        start_time = time.time()
        # keep spinning for 1 second
        while (time.time() - start_time) < 3:
            print(self.get_y_pos_inches())
            time.sleep(0.1)
        self.Y_MOTOR.stop()
        self.is_y_homed = True
        self.EN.off()

    def home_x(self, speed=0.3):
        self.EN.on()
        self.X_MOTOR.backward(speed)
        while not self.limit.is_pressed(LIMIT.X_LIM_NEG):
            print("encoder: ", self.X_ENCODER.steps)
            time.sleep(0.01)
        self.X_MOTOR.stop()
        self.X_ENCODER.value = 0

        self.X_MOTOR.forward(speed)
        start_time = time.time()
        # keep spinning for 1 second
        while (time.time() - start_time) < 3:
            print(self.get_x_pos_inches())
            time.sleep(0.1)
        self.X_MOTOR.stop()
        self.is_x_homed = True
        self.EN.off()

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
        self.EN.on()

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

