import schedule
import logging
import time
import RPi.GPIO as GPIO

# EDIT Configuration here
PUMP_RELAY_PINS = range(0, 255)

### No editing below here except when things break

SYSTEM_START = time.time()
logging.basicConfig(level=logging.DEBUG)

def init_gpio():
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)
    for pin in PUMP_RELAY_PINS:
        GPIO.setup(pin, GPIO.OUT)

def test_all_pumps():
    for pin in PUMP_RELAY_PINS:
         GPIO.output(pin,True)
         logging.debug("Turn on pump pin %s", pin)
         time.sleep(1)
         GPIO.output(pin,False)
         logging.debug("Turn off pump pin %s", pin)



init_gpio()

logging.info("Test starting")

test_all_pumps()

GPIO.cleanup()

logging.info("Test completed")