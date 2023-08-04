import schedule
import logging
import time
#import RPi.GPIO as GPIO

# EDIT Configuration here
PUMP_RELAY_PINS = { 37 }
MAX_PUMP_OPERATION = 540
EARLIEST_RUN = "08:00"
LATEST_RUN = "20:00"
DAYTIME_WAIT = 180
NIGHTTIME_WAIT = 1800

### No editing below here except when things break

SYSTEM_START = time.time()
last_pump_start = None
logging.basicConfig(level=logging.DEBUG)

earliest_run_today = None
latest_run_today = None

def start_all_pumps():
    last_pump_start = time.time()
    for pin in PUMP_RELAY_PINS:
         #GPIO.output(pin,True)
         logging.debug("Turn on pump pin %s", pin)

def stop_all_pumps():
    for pin in PUMP_RELAY_PINS:
         #GPIO.output(pin,False)
         logging.debug("Turn off pump pin %s", pin)

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
    today = time.strftime('%Y:%j', time.localtime())
    schedule.every().day.at(EARLIEST_RUN).do(FILL_TANK)
    wait = DAYTIME_WAIT
    while True: 
        if not earliest_run_today:
            earliest_run_today = time.strptime(today + " " + EARLIEST_RUN, '%Y:%j %H:%M')
            logging.debug("Reset earliest job schedule to %s", time.asctime(earliest_run_today))
        if not latest_run_today:
            latest_run_today = time.strptime(today + " " + LATEST_RUN, '%Y:%j %H:%M')
            logging.debug("Reset latest job schedule to %s", time.asctime(latest_run_today))
        if (time.strftime('%M', time.localtime()) == 00):
            # check every full hour
            # schedule.every().day.at(??).do(REFILL_TANK)
            logging.info("No jobs scheduled for the next hour")
            
        if (time.localtime() < earliest_run_today or time.localtime() > latest_run_today):
            # nighttime -- do not run
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

