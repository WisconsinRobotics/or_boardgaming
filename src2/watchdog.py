import os
import socket
import subprocess
from pathlib import Path
import sys

from gpiozero import DigitalOutputDevice
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
from dual_max_motor.dual_max14870_rpi import motors
from gpiozero.pins.pigpio import PiGPIOFactory

EN_PIN = 5
SOCKET_PATH = '/tmp/motor-watchdog.sock'
TIMEOUT = 0.5

class WatchdogClient:
    _SOCKET_PATH = "/tmp/motor-watchdog.sock"
    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self._SOCKET_PATH)
    
    def send_heartbeat(self):
        self.sock.sendall(b"1")

def main():
    
    enable = DigitalOutputDevice(EN_PIN, active_high=False, initial_value=False, pin_factory=PiGPIOFactory())
    def disable_motors():
        enable.off()

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        
        try:
            os.unlink(SOCKET_PATH)
        except FileNotFoundError:
            pass

        server.bind(SOCKET_PATH)
        server.listen()
        conn, addr = server.accept()
        conn.settimeout(0.5)
        motors.setSpeeds(0, 0)
        enable.on()

        while True:
            print("waiting for data...")
            try:
                data = conn.recv(1)
            except socket.timeout:
                print("Timeout occurred")
                break
            if not data:
                print("client disconnected")
                break
            print("received", data)
        motors.setSpeeds(0, 0)
        enable.off()

if __name__ == "__main__":
    main()