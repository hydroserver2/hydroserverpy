import os
import argparse
import scheduler
import logging
from hydroloader import HydroLoader


parser = argparse.ArgumentParser()

parser.add_argument('--confdir', help='The path to the directory where HydroLoader conf files are stored.')
parser.add_argument('--service', help='The root URL of the HydroServer SensorThings API to be used by HydroLoader.')
parser.add_argument('--auth', help='A HydroServer authentication token to allow datastream modification.')
parser.add_argument('--conffile', help='The name of a conf file which will be synced immediately in a one-off job.')
parser.add_argument('--logfile', help='The path to the log file for the application.')
parser.add_argument('--errorfile', help='The path to the error log file for the application.')
parser.add_argument('--statusfile', help='The path to the that stores statuses for datastreams.')


if __name__ == "__main__":

    args = parser.parse_args()

    hydroloader_logger = logging.getLogger('hydroloader')
    scheduler_logger = logging.getLogger('scheduler')

    hydroloader_logger.setLevel(logging.INFO)
    scheduler_logger.setLevel(logging.INFO)

    if args.logfile:
        info_log_handler = logging.FileHandler(
            filename=args.logfile, mode='a'
        )
        info_log_handler.setLevel(logging.INFO)
        hydroloader_logger.addHandler(info_log_handler)
        scheduler_logger.addHandler(info_log_handler)

    if args.errorfile:
        error_log_handler = logging.FileHandler(
            filename=args.errorfile, mode='a'
        )
        error_log_handler.setLevel(logging.ERROR)
        hydroloader_logger.addHandler(error_log_handler)
        scheduler_logger.addHandler(error_log_handler)

    if all([
        args.confdir, args.auth, args.service
    ]):
        if args.conffile:
            loader = HydroLoader(
                conf=os.path.join(args.confdir, args.conffile),
                auth=tuple(args.auth.split(',')),
                service=args.service
            )
            datastream_thru_dates = loader.sync_datastreams()

        else:
            scheduler.HydroLoaderScheduler(
                conf_dir=args.confdir,
                auth=tuple(args.auth.split(',')),
                service=args.service,
                status_file=args.statusfile
            )
            input()
