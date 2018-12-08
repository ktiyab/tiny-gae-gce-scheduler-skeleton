import re
from cron_descriptor import ExpressionDescriptor
from croniter import croniter
from datetime import datetime, timedelta
import time
from compute import instance
from .model import job as jobmodel

JOB_RUNNING_STATUS = "running"
MIN_TIME_TO_RUN = 1
JOB_DEFAULT_STATUS="standby"
SLEEP_TIME_AFTER_DATASTORE_OP = 1
STOP_AFTER_RUN_VALUE="stop"
DELETE_AFTER_RUN_VALUE="delete"

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
        return re.sub(r'\W+', '-', name)

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

    ####################################################################################
    # ********** JOBS MANIPULATION
    ####################################################################################

    # Watch jobs and start if needed
    """
        jobs: list of jobs
        job_model: job datastore model entity
        override: launch job even if it's not the time
    """
    def run(self, job_name, override):

        jobs = self.get_job_by_name(job_name)

        # Convert cron to readable before listing values
        for job in jobs:

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

            nextRunTime = self.cron_next_run(cron_schedule)
            roundedDownTime = self.roundDownTime()

            # If it's time to run or we force run
            if roundedDownTime == nextRunTime or override:

                # Check if job is already running
                if job_status != JOB_RUNNING_STATUS:
                    # Run job by initializing new client
                    new_instance = instance(project_id)
                    new_instance.run_job(job)

    """
        Watch jobs and find wich ones must be launch in MIN_TIME_TO_RUN
    """

    # Loop jobs and create queue of jobs to stop and job to run

    def overwatch(self):

        print(">>>>>>>>> Minischeduler.overwatch")

        jobs = self.get_job_list()

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

            # Add new job to the jobs queue
            if min_before <= MIN_TIME_TO_RUN:
                queue = jobmodel.Queue(project_id=project_id, machine_name=machine_name, machine_zone=machine_zone,
                                       after_run=after_run,max_running_time=max_running_time,job_name=job_name)
                queue.put()

        ####################################################
        # JOBS TO RUN STOP
        ####################################################
        queues = self.get_queue_list()

        for queue in queues:

            creation=queue.creation
            project_id=queue.project_id
            machine_name=queue.machine_name
            after_run = queue.after_run
            max_running_time = queue.max_running_time
            job_name = queue.job_name
            machine_zone=queue.machine_zone

            # Elapsed time in min of job running
            elapsed_time = self.elapsed_min_after_run(creation)
            print(elapsed_time)

            # Check job which reach max run time and stop or delete instances
            if elapsed_time - (MAX_GRACE_MIN + int(max_running_time)) >=0:

                # Stop instance if instance must be stopped
                if after_run == STOP_AFTER_RUN_VALUE:
                    new_instance = instance(project_id)
                    new_instance.stop(machine_name, machine_zone)

                # Delete instance if instance must be deleted
                if after_run == DELETE_AFTER_RUN_VALUE:
                    new_instance = instance(project_id)
                    new_instance.delete(machine_name, project_id, machine_zone)



    ####################################################################################
    # ********** INSTANCES MANIPULATION
    ####################################################################################
    """
        Stop GCE instances (and jobs)
        - jobs: list of JOB
        - job_model: model of job
    """
    def stop(self, job_name):

        jobs = self.get_job_by_name(job_name)

        # Convert cron to readable before listing values
        for job in jobs:

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
                   machine_os, cron_schedule, max_running_time, job_name):

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
            new_job.job_status = JOB_DEFAULT_STATUS
            new_job.put()

            return True

        return False

    ###################
    ## QUEUE
    ###################
    def get_queue_list(self):

        return jobmodel.Queue().get(" ORDER BY creation DESC")