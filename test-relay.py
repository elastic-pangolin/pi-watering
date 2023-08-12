import schedule
import logging
import time
import RPi.GPIO as GPIO

# EDIT Configuration here
PUMP_RELAY_PINS = { 37 }

### No editing below here except when things break

SYSTEM_START = time.time()
logging.basicConfig(level=logging.DEBUG)

def start_all_pumps():
    for pin in PUMP_RELAY_PINS:
         GPIO.output(pin,True)
         logging.debug("Turn on pump pin %s", pin)

def stop_all_pumps():
    for pin in PUMP_RELAY_PINS:
         GPIO.output(pin,False)
         logging.debug("Turn off pump pin %s", pin)

logging.info("Test starting")

start_all_pumps()
time.sleep(1)
stop_all_pumps()

logging.info("Test completed")