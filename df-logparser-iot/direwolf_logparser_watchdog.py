from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json, csv, time, datetime, os, sys
import logging
from logging.handlers import RotatingFileHandler

class DFParserUtil():
    """A class mostly to collect and organize some utility functions I plan to use in this implementation. Most of them are uwritten to be used as classmethods."""
    def __init__(self):
        pass

    @classmethod
    def get_todays_date(cls):
        current_date_time = datetime.datetime.now()
        formatted_date_time = current_date_time.strftime("%Y-%m-%d")
        return formatted_date_time
    
    @classmethod
    def setup_logger(cls, name, log_file, maxbytes, backups, level=logging.DEBUG):
        """This function is providing the configuration for the logger used in this script."""
        dfp_logger = logging.getLogger(name)
        dfp_logger.setLevel(level)
        log_handler = RotatingFileHandler(log_file, maxBytes=maxbytes, backupCount=backups)
        formatter = logging.Formatter('%(asctime)s|%(name)s|%(threadName)s|%(levelname)s|%(message)s')
        log_handler.setFormatter(formatter)
        dfp_logger.addHandler(log_handler)

        return dfp_logger
    

    
class DFParserHandler(FileSystemEventHandler):
    def __init__(self):
        
        super().__init__()
    def on_created(self, event):
        print("File created: {}".format(event.src_path))
        dfp_logger.debug("File created: {}".format(event.src_path))
        return super().on_created(event)
    def on_modified(self, event):
        print("File modified: {}".format(event.src_path))
        dfp_logger.debug("File modified: {}".format(event.src_path))
        return super().on_modified(event)

if __name__ == "__main__":
    watchdog_path = Path("./df-logparser-iot/testlogpath")
    dfp_logger = DFParserUtil.setup_logger("DFP-Logger", "./df-logparser-iot/dfp-logs/df-parser-watchdog.log",5000,4)
    dfp_observer = Observer()
    dfp_handler = DFParserHandler()
    dfp_observer.schedule(dfp_handler, watchdog_path, recursive=False)
    dfp_observer.start()

    last_line_processed = 0
    current_file = DFParserUtil.get_todays_date() + ".log"
    print("Direwolf log with today's date should be {}".format(current_file))
    dfp_logger.debug("Direwolf log with today's date should be {}".format(current_file))
    current_joined_path = os.path.join(watchdog_path, current_file)
    if os.path.isfile(current_joined_path) == False:
        print("Current day's Direwolf message log not found: {} - Please check the configuration for possible errors, then restart the service.".format(current_joined_path))
        dfp_logger.info("Current day's Direwolf message log not found: {} - Please check the configuration for possible errors, then restart the service.".format(current_joined_path))
        sys.exit(1)
    else:
        print("Current day's Direwolf message log found: {} - Service starting up...".format(current_joined_path))
        dfp_logger.info("Current day's Direwolf message log found: {} - Service starting up...".format(current_joined_path))
        

    # -- Let the program run until it is stopped. --
    while 1 == 1:
        time.sleep(1)

    dfp_observer.stop()
    dfp_observer.join()