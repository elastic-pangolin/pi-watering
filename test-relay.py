import schedule
import logging
import time
import smbus
import sys

# EDIT Configuration here
PUMP_DEVICE_IDS = range(1, 5)

### No editing below here except when things break

SYSTEM_START = time.time()
logging.basicConfig(level=logging.DEBUG)

DEVICE_BUS = 1
DEVICE_ADDR = 0x10
bus = smbus.SMBus(DEVICE_BUS)

def test_all_pumps():
    for p in PUMP_DEVICE_IDS:
         bus.write_byte_data(DEVICE_ADDR, p, 0x00)
         logging.debug("Turn on pump ID %s", p)
         time.sleep(3)
         bus.write_byte_data(DEVICE_ADDR, p, 0xFF)
         logging.debug("Turn off pump ID %s", p)


logging.info("Test starting")

test_all_pumps()

logging.info("Test completed")