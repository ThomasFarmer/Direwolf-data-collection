from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json, csv, time, datetime, os, sys
import logging
from logging.handlers import RotatingFileHandler
from direwolf_logparser_sender import DirewolfDataSender

class DFParserUtil():
    """A class mostly to collect and organize some utility functions I plan to use in this implementation. Most of them are uwritten to be used as classmethods."""
    def __init__(self):
        pass

    @classmethod
    def create_geojson_3d_point(cls, logrow):
        """Creates a single 3D GeoJSON point. This function leaves out the speed and course properties, because fixed stations are not moving objects. Altitude is stored as a third coordinate, as well as a property. """
        geojson_point = {}
        # Top level architecture
        geojson_point["type"] = "Feature"
        geojson_point["geometry"] = {}
        geojson_point["properties"] = {}
        # Setting coordinates
        geojson_point["geometry"]["type"] = "Point"
        try:
            if logrow["altitude"] == '':
                geojson_point["geometry"]["coordinates"] = [float(logrow["latitude"]), float(logrow["longitude"]), float(0.0)]
            else:
                geojson_point["geometry"]["coordinates"] = [float(logrow["latitude"]), float(logrow["longitude"]), float(logrow["altitude"])]
        except ValueError as crd_ex:
            logging.error("Exception raised while writing coordinates to GeoJSON 3D Point object, coordinates failed to convert to float: {}, {}, {}. Using default values instead.".format(logrow["longitude"],logrow["latitude"], logrow["altitude"]), crd_ex)

        # Setting metadata properties
        geojson_point["properties"]["radio_channel"] = logrow["radio_channel"]
        geojson_point["properties"]["unix_time"] = logrow["unix_time"]
        geojson_point["properties"]["iso_time"] = logrow["iso_time"]
        geojson_point["properties"]["source_addr"] = logrow["source_addr"]
        geojson_point["properties"]["station_heard"] = logrow["station_heard"]
        geojson_point["properties"]["audio_lvl"] = logrow["audio_lvl"]
        geojson_point["properties"]["error_correction"] = logrow["error_correction"]
        geojson_point["properties"]["data_type_indicator"] = logrow["data_type_indicator"]
        geojson_point["properties"]["name"] = logrow["object_name"]
        geojson_point["properties"]["aprs_symbol"] = logrow["aprs_symbol"]
        geojson_point["properties"]["frequency"] = logrow["frequency"]
        geojson_point["properties"]["altitude"] = logrow["altitude"]
        geojson_point["properties"]["tone"] = logrow["tone"]
        geojson_point["properties"]["system"] = logrow["system"]
        geojson_point["properties"]["status"] = logrow["status"]
        geojson_point["properties"]["telemetry"] = logrow["telemetry"]
        geojson_point["properties"]["comment"] = logrow["comment"]
        return geojson_point

    @classmethod
    def decode_log_row(cls, logrow):
        row_data = {}
        row_data["radio_channel"] = logrow[0]
        row_data["unix_time"] = logrow[1]
        row_data["iso_time"] = logrow[2]
        row_data["source_addr"] = logrow[3]
        row_data["station_heard"] = logrow[4]
        row_data["audio_lvl"] = logrow[5]
        row_data["error_correction"] = logrow[6]
        row_data["data_type_indicator"] = logrow[7]
        row_data["object_name"] = logrow[8]
        row_data["aprs_symbol"] = logrow[9]
        row_data["latitude"] = logrow[10]
        row_data["longitude"] = logrow[11]
        row_data["speed"] = logrow[12]
        row_data["course"] = logrow[13]
        row_data["altitude"] = logrow[14]
        row_data["frequency"] = logrow[15]
        row_data["offset"] = logrow[16]
        row_data["tone"] = logrow[17]
        row_data["system"] = logrow[18]
        row_data["status"] = logrow[19]
        row_data["telemetry"] = logrow[20]
        row_data["comment"] = logrow[21]
        return row_data
    
    @classmethod
    def get_todays_date(cls):
        current_date_time = datetime.datetime.now()
        formatted_date_time = current_date_time.strftime("%Y-%m-%d")
        return formatted_date_time
    
    @classmethod
    def save_log_file_progress(cls, progress_file, logfile, row_num):
        progress = {}
        print(progress.get(logfile))
        with open(progress_file) as f:
            progress = json.load(f)
        if progress.get(logfile) == None:
            print("log file progress data not found, writing log row: {} - {}".format(logfile, row_num))
            progress[logfile] = row_num
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=4)
        elif progress.get(logfile) == row_num:
            print("log file progress data is up to date, no need to modify file: {} - {}".format(logfile, row_num))
        elif progress.get(logfile) != row_num:
            print("log file progress data differs, updating file with following data: {} - {}".format(logfile, row_num))
            progress[logfile] = row_num
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=4)

    @classmethod
    def read_log_file_progress(cls, progress_file, logfile):
        progress = {}
        print(progress.get(logfile))
        with open(progress_file) as f:
            progress = json.load(f)
        if progress.get(logfile) == None:
            print("log file progress data not found, assuming zero progress: {}".format(logfile))
            return 0
        else:
            return progress.get(logfile)

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
    
    @classmethod
    def read_logfile_and_create_list(cls, logfile, skip_to_line=1):
        """This function creates a version of the logfile parsed into a simple list format. We use this later to avoid constant reading of the logfile from the disk."""
        log_in_list = []
        with open(logfile, newline='') as csvfile:
            logreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(logreader)
            for skip in range(0,skip_to_line-1):
                next(logreader)
            for logrow in logreader:
                lr = cls.decode_log_row(logrow=logrow)
                log_in_list.append(lr)
        return log_in_list
    

    
class DFParserHandler(FileSystemEventHandler):
    def __init__(self):
        self.progress_file_path = "./progress.json"
        self.df_data_sender = DirewolfDataSender()
        conn_res = self.df_data_sender.connect_to_aws()
        dfp_logger.debug("After attempting to connect to AWS, the following result was handed back to the client: {}".format(conn_res))
        super().__init__()
    def on_created(self, event):
        print("File created: {}".format(event.src_path))
        dfp_logger.debug("File created: {}".format(event.src_path))
        return super().on_created(event)
    def on_modified(self, event):
        print("File modified: {}".format(event.src_path))
        dfp_logger.debug("File modified: {}".format(event.src_path))
        if os.path.isfile(event.src_path):
            current_progress = DFParserUtil.read_log_file_progress(self.progress_file_path, event.src_path)
            proc_log = DFParserUtil.read_logfile_and_create_list(event.src_path, current_progress)
            dfp_logger.debug("** PROCESSING ROWS: {} , DATA: {}".format(len(proc_log),proc_log))
            for log_row in proc_log:
                gjs_point = DFParserUtil.create_geojson_3d_point(log_row)
                print(gjs_point)
                dfp_logger.info(gjs_point)
                self.df_data_sender.send_message_to_aws(gjs_point)
            DFParserUtil.save_log_file_progress(self.progress_file_path, event.src_path, current_progress + len(proc_log))
            return super().on_modified(event)
        else:
            print("not file: {}".format(event.src_path))

if __name__ == "__main__":
    dfp_logger = DFParserUtil.setup_logger("DFP-Logger", "./df-parser-watchdog.log",500000,4)
    current_file = DFParserUtil.get_todays_date() + ".log"
    print("Direwolf log with today's date should be {}".format(current_file))
    dfp_logger.debug("Direwolf log with today's date should be {}".format(current_file))
    folder_path =  os.environ['DF_LOG_PATH']
    current_joined_path = os.path.join(folder_path, current_file)
    watchdog_path = Path(current_joined_path)

    dfp_observer = Observer()
    dfp_handler = DFParserHandler()
    dfp_observer.schedule(dfp_handler, current_joined_path, recursive=False)
    dfp_observer.start()

    last_line_processed = 0

    
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
