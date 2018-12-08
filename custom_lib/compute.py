"""
Copyright Tiyab KONLAMBIGUE

Licensed under the BSD 3-Clause "New" or "Revised" license;
you may not use this file except in compliance with the License.
You may obtain a copy of the License at : https://opensource.org/licenses/BSD-3-Clause
"""
from gce import client
import logging
import time
from model import job as jobmodel

JSON_KEY_FOLDER = "./credentials/"
SLEEP_TIME_AFTER_GCE_OP = 30

images_config = [
    {
    "key-word": "ubuntu",
    "image-project" : "ubuntu-os-cloud"
    }
]

class instance():

    def __init__(self, project_id):
        self.project_id =project_id
        self.json_key_path = JSON_KEY_FOLDER + project_id + ".json"
        self.gce_client = client.get_client(json_key_file=self.json_key_path, readonly=False)


    # Check if instance exist
    def exist(self, instance_name, project):
        logging.info("Run instance exist at > %s" % time.strftime("%c"))
        instance_metadata = self.get(instance_name, project)
        if instance_metadata:
            return True
        return False

    # Check if machine is running
    def get(self, instance_name, project):
        logging.info("Run instance get at > %s" % time.strftime("%c"))
        instances = self.gce_client.list_instances(project)

        for instance in instances:
            if instance['name']== instance_name:
                return instance

        return None

    # Get instance status
    def status_of(self, instance_name, project):
        logging.info("Run instance status_of at > %s" % time.strftime("%c"))
        instance_metadata = self.get(instance_name, project)

        if instance_metadata:
            return instance_metadata["status"]
        return None


    # Create a new machine if not exist
    def create(self,project, instance_name, startup_script_path,
               bucket_id, zone, image_project, image_name,type_machine
                ):
        logging.info("Run instance create at > %s" % time.strftime("%c"))

        if not self.exist(instance_name, project):
            #Create machine
            #startup_script_path= SCRIPT_FOLDER + startup_scrip_name
            self.gce_client.create_instance(project, instance_name, startup_script_path,
                                            bucket_id, zone, image_project, image_name,type_machine)

            time.sleep(SLEEP_TIME_AFTER_GCE_OP)
            #Check if machine is created
            if self.exist(instance_name, project):
                return True
            else:
                logging.info("Unexpected error, instance is not created...")
        else:
            logging.info("Instance "+instance_name+" already exist...")

        return False

    # Stop running instance
    def stop(self, instance_name, project, zone):
        if self.exist(instance_name, project):
            current_status = self.status_of(instance_name, project)
            if current_status != "STOPPING" and \
                current_status != "TERMINATED":
                    self.gce_client.stop_instance(project, instance_name, zone)

            time.sleep(SLEEP_TIME_AFTER_GCE_OP)
            #Check is instance is stopped correctly
            if self.status_of(instance_name, project) == "TERMINATED":
                return True
        else:
            logging.info("Instance " + instance_name + " not exist...")

        return False



    # Start instance stopped
    def start(self, instance_name, project, zone):
        if self.exist(instance_name, project):
            current_status = self.status_of(instance_name, project)
            if current_status == "TERMINATED":
                self.gce_client.start_instance(project, instance_name, zone)

            time.sleep(SLEEP_TIME_AFTER_GCE_OP)
            # Check is instance is stopped correctly
            if self.status_of(instance_name, project) == "RUNNING":
                return True
        else:
            logging.info("Instance " + instance_name + " not exist...")

        return False

    # Remove instance
    def delete(self, instance_name, project, zone):

        if self.exist(instance_name, project):
            self.gce_client.delete_instance(project, instance_name, zone)

            time.sleep(SLEEP_TIME_AFTER_GCE_OP)
            # Check is instance is removed correctly
            if not self.exist(instance_name, project):
                return True
        else:
            logging.info("Instance " + instance_name + " not exist...")

        return False


    #####################################################################################################
    # JOB
    #####################################################################################################

    # Run job
    def run_job(self, job):

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

        # Check if instance exist
        # If instance exist - It's an stopped instance
        if self.exist(machine_name, project_id):
            status = self.status_of(machine_name, project_id)
            print('>>>>>> Status is ' + str(status))
            if status!="RUNNING":
                # Create job by starting instance
                # By starting up instance, startup script will do the job
                new_instance_running = self.start(machine_name, project_id, machine_zone)

                if new_instance_running:
                    # Update Datastore
                    self.update_datastore_running_job(job)
        else:
            # If instance not exist create new one

            #Find image project by machine_os
            os_project = None
            for image in images_config:
                if image["key-word"] in machine_os:
                    os_project = image["image-project"]

             # Create instance if we have image project
            if not os_project is None:
                new_instance_running = self.create(project_id,machine_name,startup_script,bucket_id,
                                       machine_zone, os_project, machine_os, machine_type)

            time.sleep(SLEEP_TIME_AFTER_GCE_OP)
            if new_instance_running:
                # Update Datastore
                self.update_datastore_running_job(job)


    # Stop job
    def stop_job(self, job):

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

        if self.exist(machine_name, project_id):

            if after_run =="stop":
                self.stop(machine_name, project_id, machine_zone)
            if after_run =="delete":
                self.delete(machine_name, project_id, machine_zone)

        current_status = self.status_of(machine_name, project_id)

        time.sleep(SLEEP_TIME_AFTER_GCE_OP)

        if current_status == "TERMINATED" or current_status ==None:
            # Update Datastore
            self.update_datastore_stopping_job(job)


    #################################################################################################
    ######## DATASTORE
    #################################################################################################

    #Update datastore and indicate a running job
    def update_datastore_running_job(self, job):
        # Check if job exist
        my_filter = "WHERE job_name='" + job.job_name + "'"
        existing_job = jobmodel.Job().get(my_filter)

        if len(existing_job) > 0:
            logging.info("update_job: Update job " + job.job_name + " to datastore ...")
            #Update existing job
            old_job = existing_job[0]

            old_job.emails = job.emails
            old_job.project_id = job.project_id
            old_job.bucket_id = job.bucket_id
            old_job.machine_name = job.machine_name
            old_job.startup_script = job.startup_script
            old_job.machine_type = job.machine_type
            old_job.machine_zone = job.machine_zone
            old_job.after_run=job.after_run
            old_job.machine_os = job.machine_os
            old_job.cron_schedule = job.cron_schedule
            old_job.max_running_time = job.max_running_time
            old_job.job_name = job.job_name
            old_job.job_status = "running"
            old_job.put()
        else:
            #Redirect to list
            logging.info("Unable to update job " + job.job_name + ", job not found ...")


    #Update datastore and indicate a stopped job
    def update_datastore_stopping_job(self, job):
        # Check if job exist
        my_filter = "WHERE job_name='" + job.job_name + "'"
        existing_job = jobmodel.Job().get(my_filter)

        if len(existing_job) > 0:
            logging.info("update_job: Update job " + job.job_name + " to datastore ...")
            #Update existing job
            old_job = existing_job[0]

            old_job.emails = job.emails
            old_job.project_id = job.project_id
            old_job.bucket_id = job.bucket_id
            old_job.machine_name = job.machine_name
            old_job.startup_script = job.startup_script
            old_job.machine_type = job.machine_type
            old_job.machine_zone = job.machine_zone
            old_job.after_run=job.after_run
            old_job.machine_os = job.machine_os
            old_job.cron_schedule = job.cron_schedule
            old_job.max_running_time = job.max_running_time
            old_job.job_name = job.job_name
            old_job.job_status = "standby"
            old_job.put()
        else:
            #Redirect to list
            logging.info("Unable to update job " + job.job_name + ", job not found ...")