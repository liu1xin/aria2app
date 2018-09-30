# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Copyright 2015 Hewlett-Packard

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys
import threading
import time

from apscheduler.schedulers import background
from oslo_config import cfg
from oslo_log import log

from dbmanager.scheduler import arguments
from dbmanager.scheduler import scheduler_job
from dbmanager.scheduler import utils
import daemon as linux_daemon

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class DBManagerScheduler(object):
    def __init__(self, interval, job_path, concurrent_jobs=1):
        # config_manager
        self.job_path = job_path
        self.lock = threading.Lock()
        job_defaults = {
            'coalesce': True,
            'max_instances': 1
        }
        executors = {
            'default': {'type': 'threadpool', 'max_workers': 1},
            'threadpool': {'type': 'threadpool',
                           'max_workers': concurrent_jobs}
        }
        self.scheduler = background.BackgroundScheduler(
            job_defaults=job_defaults,
            executors=executors)

        self.scheduler.add_job(self.poll, 'interval',
                                   seconds=interval, id='api_poll',
                                   executor='default')

        self.add_job = self.scheduler.add_job
        self.remove_job = self.scheduler.remove_job
        self.jobs = {}

    def start(self):
        self.poll()
        # schedule主线程启动,此时只包含了已注册的定时poll在default线程
        # 其他jobs通过poll注册到threadpool线程上
        self.scheduler.start()
        try:
            while True:
                # Due to the new Background scheduler nature, we need to keep
                # the main thread alive.
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but
            # should be done if possible
            self.scheduler.shutdown(wait=False)

    def is_scheduled(self, job_id):
        return self.scheduler.get_job(job_id) is not None

    def create_job(self, job_doc):
        job = scheduler_job2.Job.create(self, job_doc)
        if job:
            self.jobs[job.id] = job
            LOG.info("Created job {0}".format(job.id))
        return job

    def get_jobs(self):
        return utils.get_jobs_from_disk(self.job_path)

    def update_job(self, job_id, job_doc):
        if job_id == job_doc['job_id']:
            joblist = [job_doc]
            utils.save_jobs_to_disk(joblist, self.job_path)

    def poll(self):
        try:
            work_job_doc_list = self.get_jobs()
        except Exception as e:
            LOG.error("Unable to get jobs: {0}".format(e))
            return

        work_job_id_list = []

        # create job if necessary, then let it process its events
        for job_doc in work_job_doc_list:
            job_id = job_doc['job_id']
            work_job_id_list.append(job_id)
            job = self.jobs.get(job_id, None) or self.create_job(job_doc)
            if job:
                # 如果是废止的job则结束对应子进程
                if job_doc['job_schedule']['event'] == 'abort':
                    pid = int(job_doc['job_schedule']['current_pid'])
                    utils.terminate_subprocess(pid, 'freezer-agent')
                # job处理自己的event
                job.process_event(job_doc)

        # 可能有不在的job则移除掉
        for job_id, job in self.jobs.items():
            if job_id not in work_job_id_list:
                job.remove()

        remove_list = [job_id for job_id, job in self.jobs.items()
                       if job.can_be_removed()]

        for k in remove_list:
            self.jobs.pop(k)

    def stop(self):
        sys.exit()

    def reload(self):
        LOG.warning("reload not supported")


def main():
    possible_actions = ['start', 'stop', 'restart', 'status', 'reload']

    arguments.parse_args(possible_actions)
    arguments.setup_logging()

    if CONF.action not in possible_actions:
        CONF.print_help()
        return 65  # os.EX_DATAERR

    utils.create_dir(CONF.jobs_dir, do_log=False)
    dbmanager_scheduler = DBManagerScheduler(interval=int(CONF.interval),
                                            job_path=CONF.jobs_dir,
                                            concurrent_jobs=CONF.concurrent_jobs)
    if CONF.no_daemon:
        daemon = linux_daemon.NoDaemon(daemonizable=dbmanager_scheduler)
    else:
        daemon = linux_daemon.Daemon(daemonizable=dbmanager_scheduler)

    if CONF.action == 'start':
        daemon.start()
    elif CONF.action == 'stop':
        daemon.stop()
    elif CONF.action == 'restart':
        daemon.restart()
    elif CONF.action == 'reload':
        daemon.reload()
    elif CONF.action == 'status':
        daemon.status()

    # os.RETURN_CODES are only available to posix like systems, on windows
    # we need to translate the code to an actual number which is the equivalent
    return 0  # os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
