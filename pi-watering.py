import schedule
import logging
import time
import math
import sys

# optional dependency only available on raspberry pi
try:
    import smbus
except ImportError:
    smbus = None

# EDIT Configuration here #TODO: read from env
MAX_PUMP_OPERATION = 540
EARLIEST_RUN = "08:00"
LATEST_RUN = "20:00"
DAYTIME_WAIT = 180
NIGHTTIME_WAIT = 1800

### No editing below here except when things break

SYSTEM_START = 0

# simlate the bus for debugging
class Simbus():
    def __init__(self):
        ...

    def write_byte_data(self, addr, did, byte):
        logging.debug(f"Simulate Relais Bus - Written to {addr} at ID {did}: {byte}")

class Pumpmanagement():
    def __init__(self, simulate: bool = False):
        self.last_pump_start = None
        self.earliest_run_today = None
        self.latest_run_today = None
        self.DEVICE_BUS = 1
        self.DEVICE_ADDR = 0x10
        self.PUMP_DEVICE_IDS = (1, 2)
        if simulate or not smbus:
            self.bus = Simbus()
        else:
            self.bus = smbus.SMBus(DEVICE_BUS)

    def set_earliest_run_today(self, new_time):
        self.earliest_run_today = new_time

    def set_latest_run_today(self, new_time):
        self.latest_run_today = new_time

    def start_all_pumps(self):
        self.last_pump_start = time.time()
        for p in self.PUMP_DEVICE_IDS:
            self.bus.write_byte_data(self.DEVICE_ADDR, p, 0x00)
            logging.debug("Turn on pump pin %s", p)

    def stop_all_pumps(self):
        for p in self.PUMP_DEVICE_IDS:
            self.bus.write_byte_data(self.DEVICE_ADDR, p, 0xFF)
            logging.debug("Turn off pump pin %s", p)

    def FILL_TANK(self):
        logging.info("Starting FILL_TANK job")
        if self.last_pump_start and self.last_pump_start >= time.time() - MAX_PUMP_OPERATION * 2:
            # last pump start too recent, sleep
            pump_backoff_wait = self.last_pump_start + MAX_PUMP_OPERATION * 2 - time.time()
            logging.debug("Pump start delayed due to minimum backoff, waiting for %s seconds", pump_backoff_wait)
            time.sleep(pump_backoff_wait)
        pump_checkin_wait = 5
        max_cycles = math.ceil(MAX_PUMP_OPERATION / pump_checkin_wait)
        start_time = time.time()
        self.start_all_pumps()
        for i in range(max_cycles):
            time.sleep(pump_checkin_wait)
            seconds_passed = time.time() - start_time
            if seconds_passed >= MAX_PUMP_OPERATION:
                 break
        self.stop_all_pumps()
        logging.info("Completed FILL_TANK job")

    def REFILL_TANK():
        # run fill tank once
        self.FILL_TANK()
        return schedule.CancelJob

def infolog():
    seconds_since = time.time() - SYSTEM_START
    logging.info("Operating for %s seconds", math.floor(seconds_since))
    logging.info(schedule.get_jobs())

def main():
    args = sys.argv[1:]
    arg_simulate = False
    for arg in args:
        if arg == "-simulate" or arg == "-s":
            arg_simulate = True

    SYSTEM_START = time.time()
    logging.basicConfig(
      format='%(asctime)s [%(levelname)s] %(message)s',
      level=logging.DEBUG,
      datefmt='%H:%M:%S'
    )
    try:
        pumpmgmt = Pumpmanagement(simulate=arg_simulate)
        logging.info("Script starting on %s (%s)", time.strftime('%H:%M:%S %Y, day %j', time.localtime()),
          time.strftime('%s', time.localtime()) )
        # reset all relays
        pumpmgmt.stop_all_pumps()
    except Exception as e:
        logging.error("Something went wrong during system initialization!")
        logging.error(e)
        return

    today = time.strftime('%Y:%j', time.localtime())
    hour = time.strftime('%H', time.localtime())
    last_hour = hour
    schedule.every().day.at(EARLIEST_RUN).do(pumpmgmt.FILL_TANK)
    infolog()
    while True:
        wait = DAYTIME_WAIT
        if not pumpmgmt.earliest_run_today:
            pumpmgmt.set_earliest_run_today(time.strptime(today + " " + EARLIEST_RUN, '%Y:%j %H:%M'))
            logging.debug("Reset earliest job schedule to %s", time.asctime(pumpmgmt.earliest_run_today))
        if not pumpmgmt.latest_run_today:
            pumpmgmt.set_latest_run_today(time.strptime(today + " " + LATEST_RUN, '%Y:%j %H:%M'))
            logging.debug("Reset latest job schedule to %s", time.asctime(pumpmgmt.latest_run_today))

        if (time.localtime() < pumpmgmt.earliest_run_today or time.localtime() > pumpmgmt.latest_run_today):
            # nighttime -- do not run
            logging.debug("Script is in nightmode")
            wait = NIGHTTIME_WAIT
            today = time.strftime('%Y:%j', time.localtime())
            pumpmgmt.set_earliest_run_today(None)
            pumpmgmt.set_latest_run_today(None)
        else:
            last_hour = hour
            hour = time.strftime('%H', time.localtime())
            if (hour != last_hour):
                # schedule refills etc here
                logging.info("No new jobs have been scheduled")

            infolog()
            try: 
                schedule.run_pending()
            except Exception as e:
                pumpmgmt.stop_all_pumps()
                logging.error(e)

            time.sleep(wait)

    schedule.clear()

if __name__ == "__main__":
    main()
