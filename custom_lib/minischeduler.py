"""
Copyright Tiyab KONLAMBIGUE

Licensed under the BSD 3-Clause "New" or "Revised" license;
you may not use this file except in compliance with the License.
You may obtain a copy of the License at : https://opensource.org/licenses/BSD-3-Clause
"""

import re
from cron_descriptor import ExpressionDescriptor
from croniter import croniter
from datetime import datetime, timedelta
import time
from compute import instance
from .model import job as jobmodel
import logging
import decimal


JOB_RUNNING_STATUS = "running"
MIN_TIME_TO_RUN = 1
JOB_DEFAULT_STATUS="standby"
SLEEP_TIME_AFTER_DATASTORE_OP = 1
STOP_AFTER_RUN_VALUE="stop"
DELETE_AFTER_RUN_VALUE="delete"

GCE_TERMINATED_STATUS = "TERMINATED"
GCE_RUNNING_STATUS    = "RUNNING"

"""
                <option value="f1-micro">f1-micro</option>
                <option value="g1-small">g1-small</option>
                <option value="n1-highcpu-8">n1-highcpu-8</option>
                <option value="n1-highmem-2">n1-highmem-2</option>
"""
# Estimated hourly pricing at 2018/12
GCE_PRINCING = {
    "f1-micro":"0.0076",
    "g1-small":"0.0257",
    "n1-highcpu-8":"0.2836",
    "n1-highmem-2":"0.1184"
}
GCE_PRINCING_CURRENCY = "$"


# More minute add to wait before stopping or deleting instance
MAX_GRACE_MIN = 5


"""
            creation = job.creation
            updated = job.updated
            emails = job.emails
            project_id = job.project_id
            bucket_id = job.bucket_id
            machine_name = job.machine_name
            startup_script = job.startup_script
            machine_type = job.machine_type
            machine_zone = job.machine_zone
            machine_os = job.machine_os
            cron_schedule = job.cron_schedule
            after_run = job.after_run
            max_running_time = job.max_running_time
            job_name = job.job_name
            job_status = job.job_status
            last_run = job.last_run
"""
class utils():

    ####################################################################################
    # ********** CRONTAB MANIPULATION
    ####################################################################################

    # Return valid instance name
    def valid_instance_name(self, name):
        return re.sub(r'\W+', '-', name.lower())

    def readable_cron(self, value):
        return str(ExpressionDescriptor(value))

    def cron_next_run(self, value):
        iter = croniter(value, datetime.now())
        return iter.get_next(datetime)

    def cron_previous_run(self, value):
        iter = croniter(value, datetime.now())
        return iter.get_prev(datetime)


    def is_cron_valid(self, value):
        return croniter.is_valid(value)

    def delay_before_next_run(self, value):
        d = datetime.now()
        iter = croniter(value, d)
        return (iter.get_next(datetime) - d) * 24 * 60

    """
        Round time down to the top of the previous minute
    """
    def roundDownTime(self,dt=None, dateDelta=timedelta(minutes=1)):
        roundTo = dateDelta.total_seconds()
        if dt == None: dt = datetime.now()
        seconds = (dt - dt.min).seconds
        rounding = (seconds + roundTo / 2) // roundTo * roundTo
        return dt + timedelta(0, rounding - seconds, -dt.microsecond)

    """
        Get number of min remaining before the next run
    """
    def min_before_next_run(self, cron_schedule):

        next_run_time = self.cron_next_run(cron_schedule)
        current_time = self.roundDownTime()
        diff = next_run_time - current_time
        return (diff.days * 24 * 60) + (diff.seconds / 60)

    """
        Get number of min after a run
    """
    def elapsed_min_after_run(self, run_time):
        current_time = self.roundDownTime()
        diff = current_time - run_time
        return (diff.days * 24 * 60) + (diff.seconds / 60)


    def is_job_config_valid(self, emails, cron_schedule, max_running_time):

        message = ""
        #Check crontab
        if not self.is_cron_valid(cron_schedule):
            message = message + "\n Cron value is not valid, please correct the value."

        # Check if emails is valid
        emails_list = emails.split(",")

        for email in emails_list:
            if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email) == None:
                message = message + "\n Email is not valid email, please correct your email."

        # Check is max run time in minute is valide number
        try:
            int(max_running_time)+1
        except ValueError:
            message = message + "\n Value of max run time (in minute) is not valid."
            pass

        return message

    ####################################################################################
    # ********** JOBS MANIPULATION
    ####################################################################################

    # Watch jobs and start if needed
    """
        jobs: list of jobs
        job_model: job datastore model entity
    """
    def run(self, job_name):

        jobs = self.get_job_by_name(job_name)
        for job in jobs:

            project_id = job.project_id
            job_status = job.job_status

            # Check if job is already running
            print(">>>>>>>> Run status is "+ job_status)
            if job_status != JOB_RUNNING_STATUS:
                # Run job by initializing new client
                new_instance = instance(project_id)
                new_instance.run_job(job)
                last_run = datetime.utcnow()
                self.update_job(job.job_name, job.emails, job.project_id, job.bucket_id, job.machine_type,
                                job.machine_name, job.startup_script, job.machine_zone, job.after_run,
                                job.machine_os, job.cron_schedule, job.max_running_time, job_name, last_run, JOB_RUNNING_STATUS)

    """
        Watch jobs and find wich ones must be launch in MIN_TIME_TO_RUN
    """

    # Loop jobs and create queue of jobs to stop and job to run

    def overwatch(self):

        jobs = self.get_job_list()

        ####################################################
        # JOBS TO STOP FROM QUEUE
        ####################################################
        queues = self.get_queue_list()

        for queue in queues:

            creation = queue.creation
            project_id = queue.project_id
            machine_name = queue.machine_name
            after_run = queue.after_run
            max_running_time = queue.max_running_time
            machine_zone = queue.machine_zone
            job_name = queue.job_name

            # Elapsed time in min of job running
            elapsed_time = self.elapsed_min_after_run(creation)
            print(elapsed_time)
            print(elapsed_time - (MAX_GRACE_MIN + int(max_running_time)))

            # Check job which reach max run time and stop or delete instances
            if elapsed_time - (MAX_GRACE_MIN + int(max_running_time)) >= 0:

                # Stop instance if instance must be stopped
                if after_run == STOP_AFTER_RUN_VALUE:
                    new_instance = instance(project_id)
                    new_instance.stop(machine_name, project_id, machine_zone)

                # Delete instance if instance must be deleted
                if after_run == DELETE_AFTER_RUN_VALUE:
                    new_instance = instance(project_id)
                    new_instance.delete(machine_name, project_id, machine_zone)

                # Remove from Queue
                self.delete_queue(queue)
                # Set job status to standby
                self.queue_update_job(job_name)

        ####################################################
        # JOBS TO RUN QUEUE
        ####################################################

        for job in jobs:

            project_id=job.project_id
            machine_name=job.machine_name
            cron_schedule = job.cron_schedule
            after_run = job.after_run
            max_running_time = job.max_running_time
            job_name = job.job_name
            machine_zone=job.machine_zone

            # remaining Time In Min For Next Run
            min_before = self.min_before_next_run(cron_schedule)
            print(">>>>> Min before "+str(min_before))

            # Add new job to the jobs queue -- Min time to run is the latence between processing and effectif run
            if min_before <= MIN_TIME_TO_RUN:
                self.create_queue(project_id, machine_name, machine_zone, after_run, max_running_time, job_name)

        # After creating queue, run queue
        self.run_job_queue()


    def run_job_queue(self):

        queues = self.get_queue_list()

        for queue in queues:
            machine_name=queue.machine_name
            machine_zone=queue.machine_zone
            project_id=queue.project_id
            after_run = queue.after_run
            job_name = queue.job_name

            # Restart instance if instance has been stopped
            if after_run == STOP_AFTER_RUN_VALUE:

                #Check if instance exist
                new_instance = instance(project_id)
                status_of_instance = new_instance.status_of(machine_name, project_id)

                if status_of_instance == GCE_TERMINATED_STATUS:
                    new_instance.start(machine_name, project_id, machine_zone)

                # TODO: Warning we must act to alert user -- but maybe user start job manually
                if status_of_instance==GCE_RUNNING_STATUS:
                    logging.info("Trying to start GCE engine already running")

            # Delete instance if instance must be deleted
            if after_run == DELETE_AFTER_RUN_VALUE:
                #Check if instance exist
                new_instance = instance(project_id)
                status_of_instance = new_instance.status_of(machine_name, project_id)

                if status_of_instance == None:
                    # Run job
                    self.run(job_name)



    ####################################################################################
    # *****  INSTANCES MANIPULATION
    ####################################################################################

    """
        Get instance pricing
    """
    def get_estimate_running_cost(self, machine_type, max_run_time):

        hourly_cost  = GCE_PRINCING[machine_type]

        cost = (((int(max_run_time)+MAX_GRACE_MIN) * float(hourly_cost))/ 60)

        return decimal.Decimal(cost).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_UP)

    def formated_estimate_running_cost(self, machine_type, max_run_time):
        cost = self.get_estimate_running_cost(machine_type, max_run_time)
        return str(cost) + GCE_PRINCING_CURRENCY

    """
        Stop GCE instances (and jobs)
        - jobs: list of JOB
        - job_model: model of job
    """
    def stop(self, job_name):

        jobs = self.get_job_by_name(job_name)

        # Convert cron to readable before listing values
        for job in jobs:

            project_id = job.project_id
            job_status = job.job_status

        # Check if job is already running
        if job_status == JOB_RUNNING_STATUS:
            # Stop job by initializing new client
            new_instance = instance(project_id)
            new_instance.stop_job(job)
    """
    Get specified instance status
     - instance_name: GCE instance name
     - project_id: GCP project_id
     - job_status: Job status
    """
    def instance_status(self, instance_name, project_id, job_status):
        new_instance = instance(project_id)

        status_of_instance =  new_instance.status_of(instance_name, project_id)

        # Job is running on running instance
        if status_of_instance == "RUNNING" and job_status=="running":
            return "running"

        # We don't have any job running but instance is in running mode
        # May be a disfonctionnement > Stop gce manually
        if status_of_instance == "RUNNING" and job_status!="running":
            return "standby-gce-running"

        # Instance is stopped and not suppressed
        # While job is supposed to run may be job failed
        if status_of_instance == "TERMINATED" and job_status=="running":
            return "failed"

        # Instance doesn't exist
        # While job is supposed to run may be job failed
        if status_of_instance == None and job_status=="running":
            return "failed"

        # Instance is stopped and not suppressed
        if status_of_instance == "TERMINATED" and job_status!="running":
            return "standby-gce"

        return None

    def instance_stop(self, instance_name, project_id, zone):
        new_instance = instance(project_id)
        new_instance.stop(instance_name, project_id, zone)



    ####################################################################################
    # ********** DATASTORE MANIPULATION
    ####################################################################################

    ###################
    ## JOBS
    ###################

    def get_job_list(self):

        return jobmodel.Job().get(" ORDER BY updated DESC")

    def get_job_by_name(self,job_name):

        my_filter = "WHERE job_name='" + job_name + "'"
        return jobmodel.Job().get(my_filter)

    def create_job(self, emails, project_id, bucket_id, machine_type,
                   machine_name, startup_script, machine_zone, after_run,
                   machine_os, cron_schedule, max_running_time, job_name):

        new_job = jobmodel.Job(emails=emails, project_id=project_id, bucket_id=bucket_id,
                          machine_name=self.valid_instance_name(machine_name), startup_script=startup_script,
                          machine_type=machine_type, machine_zone=machine_zone, after_run=after_run,
                          machine_os=machine_os,cron_schedule=cron_schedule, max_running_time=max_running_time,
                          job_name=job_name,job_status=JOB_DEFAULT_STATUS)

        new_job.put()

        time.sleep(SLEEP_TIME_AFTER_DATASTORE_OP)

        if len(self.get_job_by_name(job_name)) >0:
            return True
        else:
            return False



    def delete_job(self,job):

        job_sup = job[0]

        job_sup.key.delete()

        time.sleep(SLEEP_TIME_AFTER_DATASTORE_OP)

        if len(self.get_job_by_name(job[0].job_name)) >0:
            return True
        else:
            return False

    def update_job(self,job_to_update_name,emails, project_id, bucket_id, machine_type,
                   machine_name, startup_script, machine_zone, after_run,
                   machine_os, cron_schedule, max_running_time, job_name, last_run, status=None):

        if status == None:
            status = JOB_DEFAULT_STATUS

        existing_job = self.get_job_by_name(job_to_update_name)

        if len(existing_job) > 0:
            new_job = existing_job[0]
            new_job.emails = emails
            new_job.project_id = project_id
            new_job.bucket_id = bucket_id
            new_job.machine_name = self.valid_instance_name(machine_name)
            new_job.startup_script = startup_script
            new_job.machine_type = machine_type
            new_job.machine_zone = machine_zone
            new_job.after_run = after_run
            new_job.machine_os = machine_os
            new_job.cron_schedule = cron_schedule
            new_job.max_running_time = max_running_time
            new_job.job_name = job_name
            new_job.job_status = status
            new_job.last_run=last_run
            new_job.put()

            return True

        return False



    ###################
    ## QUEUE
    ###################
    def get_queue_list(self):

        return jobmodel.Queue().get(" ORDER BY creation DESC")

    def create_queue(self, project_id, machine_name, machine_zone, after_run, max_running_time, job_name):
        queue = jobmodel.Queue(project_id=project_id, machine_name=machine_name, machine_zone=machine_zone,
                               after_run=after_run, max_running_time=max_running_time, job_name=job_name)
        queue.put()

    def delete_queue(self, queue):
        queue.key.delete()


    def queue_update_job(self, job_name):

        existing_job = self.get_job_by_name(job_name)

        if len(existing_job) > 0:
            new_job = existing_job[0]
            new_job.emails = new_job.emails
            new_job.project_id = new_job.project_id
            new_job.bucket_id = new_job.bucket_id
            new_job.machine_name = self.valid_instance_name(new_job.machine_name)
            new_job.startup_script = new_job.startup_script
            new_job.machine_type = new_job.machine_type
            new_job.machine_zone = new_job.machine_zone
            new_job.after_run = new_job.after_run
            new_job.machine_os = new_job.machine_os
            new_job.cron_schedule = new_job.cron_schedule
            new_job.max_running_time = new_job.max_running_time
            new_job.job_name = new_job.job_name
            new_job.job_status = JOB_DEFAULT_STATUS
            new_job.last_run=new_job.last_run
            new_job.put()

            return True

        return False