import os
import yaml
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from pytz import utc
from hydroloader import HydroLoader, HydroLoaderConf
from models import FileStreamStatus, DatastreamStatus


logger = logging.getLogger('scheduler')


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


class HydroLoaderScheduler:

    def __init__(self, conf_dir, auth, service, status_file=None):
        self.scheduler = BackgroundScheduler(timezone=utc)
        self.scheduler.add_job(
            lambda: self.update_file_streams(),
            id='hydroloader-scheduler',
            trigger='interval',
            seconds=10,
            next_run_time=datetime.utcnow()
        )
        self.conf_dir = conf_dir
        self.auth = auth
        self.status_file = status_file
        self.service = service
        self.scheduled_jobs = {}
        self.scheduler.start()

    def get_file_stream_confs(self):
        """"""

        file_stream_confs = {}

        for filename in os.listdir(self.conf_dir):
            file = os.path.join(self.conf_dir, filename)

            if os.path.isfile(file) and filename.endswith('.yaml'):
                try:
                    with open(file, 'r') as conf_file:
                        file_stream_confs[filename.replace('.yaml', '')] = HydroLoaderConf.parse_obj(
                            yaml.safe_load(conf_file)
                        )
                except Exception as e:
                    logger.error(f'Failed to parse conf file {filename} with error: {e}')
                    file_stream_confs[filename.replace('.yaml', '')] = None

        return file_stream_confs

    def get_file_stream_statuses(self):
        """"""

        file_stream_statuses = {}

        with open(self.status_file, 'r') as status_file:
            hydroloader_status = yaml.safe_load(status_file)

            if hydroloader_status:
                for file_stream_name, file_stream_status in hydroloader_status.items():
                    try:
                        file_stream_statuses[file_stream_name] = FileStreamStatus(
                            **file_stream_status
                        )
                    except:
                        file_stream_statuses[file_stream_name] = None

        return file_stream_statuses

    def update_file_stream_statuses(self, file_stream_statuses):
        file_stream_statuses_dict = {}

        for file_stream_status_name, file_stream_status in file_stream_statuses.items():
            file_stream_statuses_dict[file_stream_status_name] = file_stream_status.dict()

        with open(self.status_file, 'w') as status_file:
            yaml.dump(
                file_stream_statuses_dict,
                status_file,
                sort_keys=False,
                default_flow_style=False,
                Dumper=NoAliasDumper
            )

    def update_file_streams(self):
        """"""

        file_stream_confs = self.get_file_stream_confs()
        file_stream_statuses = self.get_file_stream_statuses()

        for file_stream_status in list(file_stream_statuses.keys() - file_stream_confs.keys()):
            if self.scheduler.get_job(file_stream_status):
                self.scheduler.remove_job(file_stream_status)
            self.scheduled_jobs.pop(file_stream_status, None)
            file_stream_statuses.pop(file_stream_status, None)

        for file_stream_conf in list(file_stream_confs.keys() - file_stream_statuses.keys()) + \
                list(set(file_stream_confs.keys()) & set(file_stream_statuses.keys())):
            self.update_schedule(file_stream_conf, file_stream_confs[file_stream_conf])
            if file_stream_statuses.get(file_stream_conf):
                file_stream_statuses[file_stream_conf].file_path = file_stream_confs[file_stream_conf].file_access.path if file_stream_confs[file_stream_conf] else None
                file_stream_statuses[file_stream_conf].valid_conf = True if file_stream_confs[file_stream_conf] is not None else False
                file_stream_statuses[file_stream_conf].next_sync = self.scheduler.get_job(file_stream_conf).next_run_time if self.scheduler.get_job(file_stream_conf) else None
            else:
                file_stream_statuses[file_stream_conf] = FileStreamStatus(
                    file_path=file_stream_confs[file_stream_conf].file_access.path if file_stream_confs[file_stream_conf] else None,
                    valid_conf=True if file_stream_confs[file_stream_conf] is not None else False,
                    next_sync=self.scheduler.get_job(file_stream_conf).next_run_time if self.scheduler.get_job(file_stream_conf) else None
                )
        self.update_file_stream_statuses(file_stream_statuses)

    def update_schedule(self, file_stream_conf_name, file_stream_conf):
        """"""

        if file_stream_conf_name in self.scheduled_jobs.keys():
            if self.scheduled_jobs[file_stream_conf_name] == self.build_schedule_string(file_stream_conf):
                return
            else:
                self.scheduled_jobs.pop(file_stream_conf_name, None)
                self.scheduler.remove_job(file_stream_conf_name)

        if file_stream_conf and file_stream_conf.schedule is not None and (
                file_stream_conf.schedule.crontab or file_stream_conf.schedule.interval
        ):
            schedule_range = {}

            if file_stream_conf.schedule.start_time:
                schedule_range['start_time'] = file_stream_conf.schedule.start_time
            if file_stream_conf.schedule.end_time:
                schedule_range['end_time'] = file_stream_conf.schedule.end_time

            if file_stream_conf.schedule.crontab:
                self.scheduler.add_job(
                    lambda: self.sync_datastreams(file_stream_conf_name),
                    CronTrigger.from_crontab(file_stream_conf.schedule.crontab, timezone='UTC'),
                    id=file_stream_conf_name,
                    **schedule_range
                )

            elif file_stream_conf.schedule.interval:
                self.scheduler.add_job(
                    lambda: self.sync_datastreams(file_stream_conf_name),
                    IntervalTrigger(
                        timezone='UTC',
                        **{file_stream_conf.schedule.interval_units: file_stream_conf.schedule.interval}
                    ),
                    id=file_stream_conf_name,
                    **schedule_range
                )

            self.scheduled_jobs[file_stream_conf_name] = self.build_schedule_string(file_stream_conf)

    @staticmethod
    def build_schedule_string(file_stream_conf):
        """"""

        if not file_stream_conf or not file_stream_conf.schedule:
            return ''

        if file_stream_conf.schedule.crontab:
            return '|'.join([
                str(file_stream_conf.schedule.start_time),
                str(file_stream_conf.schedule.end_time),
                str(file_stream_conf.schedule.crontab)
            ])
        else:
            return '|'.join([
                str(file_stream_conf.schedule.start_time),
                str(file_stream_conf.schedule.end_time),
                str(file_stream_conf.schedule.interval),
                str(file_stream_conf.schedule.interval_units)
            ])

    def sync_datastreams(self, file_stream_conf_name):
        """"""

        conf_path = os.path.join(self.conf_dir, f'{file_stream_conf_name}.yaml')
        logger.info(f'Syncing datastreams for conf file: {conf_path}')

        try:
            file_stream_statuses = self.get_file_stream_statuses()
            file_stream_status = file_stream_statuses[file_stream_conf_name]
        except:
            file_stream_statuses = None
            file_stream_status = None

        try:
            loader = HydroLoader(
                conf=conf_path,
                auth=self.auth,
                service=self.service
            )
        except Exception as e:
            logger.error(f'Conf file {conf_path} failed to initialize with error: {e}')
            return

        try:
            sync_results = loader.sync_datastreams()
        except Exception as e:
            logger.error(f'Conf file {conf_path} job failed with error: {e}')
            sync_results = None

        if file_stream_status:
            try:
                file_stream_status.last_synced = str(datetime.utcnow())
                file_stream_status.last_sync_successful = True if sync_results is not None else False
                file_stream_status.next_sync = str(self.scheduler.get_job(file_stream_conf_name).next_run_time)
                datastream_statuses = {}
                if sync_results is not None:
                    for datastream_id, result in sync_results.items():
                        datastream_statuses[str(datastream_id)] = DatastreamStatus(
                            file_thru_date=result['file_thru'],
                            database_thru_date=result['database_thru'],
                            last_sync_successful=result['success']
                        )
                    file_stream_status.datastreams = datastream_statuses
                file_stream_statuses[file_stream_conf_name] = file_stream_status
                self.update_file_stream_statuses(file_stream_statuses)
            except Exception as e:
                logger.error(f'Status update for conf file {conf_path} failed with error: {e}')


# scheduler = HydroLoaderScheduler(
#     conf_dir='/Users/klippold/hydroloader/conf',
#     auth=('test', 'test'),
#     service='http://hydroserver-dev.ciroh.org/sensorthings/v1.1',
#     status_file='/Users/klippold/hydroloader/status.yaml'
# )
# input()
