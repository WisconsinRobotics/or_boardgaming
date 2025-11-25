import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

OUT_PIN = 20   # drives LOW
IN_PIN  = 16   # reads switch state

# Drive GPIO20 LOW
GPIO.setup(OUT_PIN, GPIO.OUT)
GPIO.output(OUT_PIN, GPIO.LOW)

# Read GPIO16, using a pull-up resistor
GPIO.setup(IN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Monitoring switch between GPIO20 and GPIO16...")

try:
    while True:
        if GPIO.input(IN_PIN) == GPIO.LOW:
            print("Switch PRESSED")
        else:
            print("Switch not pressed")

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
