import socket
import time
import random
from watchdog import WatchdogClient


if __name__ == "__main__":
    client = WatchdogClient()
    while True:
        client.send_heartbeat()
        time.sleep(random.random() * 0.51)
