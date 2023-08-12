import schedule
import logging
import time
import smbus
import sys

# EDIT Configuration here
PUMP_DEVICE_IDS = (1, 2)
MAX_PUMP_OPERATION = 540
EARLIEST_RUN = "08:00"
LATEST_RUN = "20:00"
DAYTIME_WAIT = 180
NIGHTTIME_WAIT = 1800

### No editing below here except when things break

SYSTEM_START = time.time()
last_pump_start = None
logging.basicConfig(level=logging.DEBUG)

DEVICE_BUS = 1
DEVICE_ADDR = 0x10
bus = smbus.SMBus(DEVICE_BUS)

earliest_run_today = None
latest_run_today = None

def start_all_pumps():
    last_pump_start = time.time()
    for p in PUMP_DEVICE_IDS:
        bus.write_byte_data(DEVICE_ADDR, p, 0x00)
        logging.debug("Turn on pump pin %s", p)

def stop_all_pumps():
    for p in PUMP_DEVICE_IDS:
        bus.write_byte_data(DEVICE_ADDR, p, 0xFF)
        logging.debug("Turn off pump pin %s", p)

def FILL_TANK():
    logging.debug("Starting FILL_TANK job")
    if last_pump_start and last_pump_start >= time.time() - MAX_PUMP_OPERATION * 2:
        # last pump start too recent, sleep
        time.sleep(last_pump_start + MAX_PUMP_OPERATION * 2 - time.time())
    max_cycles = 100
    start_time = time.time()
    start_all_pumps()
    for i in range(max_cycles):
        time.sleep(5)
        seconds_passed = time.time() - start_time
        if seconds_passed >= MAX_PUMP_OPERATION:
             break
    stop_all_pumps()

def REFILL_TANK():
    # run fill tank once
    FILL_TANK()
    return schedule.CancelJob

def infolog():
    seconds_since = time.time() - SYSTEM_START
    logging.info("Operating for %s seconds", seconds_since)
    logging.info(schedule.get_jobs())

try:
    logging.info("Script starting on %s (%s)", time.strftime('%H:%M:%s %Y, %j', time.localtime()), time.localtime())
    today = time.strftime('%Y:%j', time.localtime())
    schedule.every().day.at(EARLIEST_RUN).do(FILL_TANK)
    infolog()
    while True:
        wait = DAYTIME_WAIT
        if not earliest_run_today:
            earliest_run_today = time.strptime(today + " " + EARLIEST_RUN, '%Y:%j %H:%M')
            logging.debug("Reset earliest job schedule to %s (%s)", time.asctime(earliest_run_today), earliest_run_today)
        if not latest_run_today:
            latest_run_today = time.strptime(today + " " + LATEST_RUN, '%Y:%j %H:%M')
            logging.debug("Reset latest job schedule to %s (%s)", time.asctime(latest_run_today), latest_run_today)
            
        logging.debug("NOW: %s", time.localtime())
        if (time.localtime() < earliest_run_today or time.localtime() > latest_run_today):
            # nighttime -- do not run
            logging.debug("Script is in nightmode")
            wait = NIGHTTIME_WAIT
            today = time.strftime('%Y:%j', time.localtime())
            earliest_run_today = None
            latest_run_today =  None
        else:
            infolog()
            schedule.run_pending()
        time.sleep(wait)
        
except Exception as e:
    logging.error(e)

schedule.clear()


