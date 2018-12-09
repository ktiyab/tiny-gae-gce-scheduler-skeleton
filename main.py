"""
Copyright Tiyab KONLAMBIGUE

Licensed under the BSD 3-Clause "New" or "Revised" license;
you may not use this file except in compliance with the License.
You may obtain a copy of the License at : https://opensource.org/licenses/BSD-3-Clause
"""

import logging
from flask import Flask, render_template, request, redirect, url_for
from custom_lib import minischeduler
import time


app = Flask(__name__)
app_utils = minischeduler.utils()

# Home page
@app.route('/')
def index():
    #jobs = job.Job().get(" ORDER BY updated DESC")
    jobs = app_utils.get_job_list()

    if len(jobs) >0:
        return redirect(url_for('list_job'))
    else:
        return redirect(url_for('form_job'))

@app.route('/form_job')
def form_job():
    logging.info("Run form_job at > %s" % time.strftime("%c"))
    return render_template('form.html',
       machine_type_value="f1-micro",
       machine_os_value="ubuntu-1604-xenial-v20181204",
       machine_zone_value="europe-west1-b",
       after_run_value="delete",
       operation="Create job",
       operation_type="None",
       old_name="None"
    )

# Submit a job
@app.route('/submit_job', methods=['POST'])
def submit_job():

    logging.info("Run submit_job at > %s" % time.strftime("%c"))

    emails = request.form['emails'].strip()
    project_id = request.form['project_id'].strip()
    bucket_id = request.form['bucket_id'].strip()
    machine_name = request.form['machine_name'].strip()
    startup_script = request.form['startup_script'].strip()
    shutdown_script = request.form['shutdown_script'].strip()
    machine_type = request.form['machine_type'].strip()
    machine_zone = request.form['machine_zone'].strip()
    after_run= request.form['after_run'].strip()
    machine_os = request.form['machine_os'].strip()
    cron_schedule = request.form['cron_schedule'].strip()
    max_running_time = request.form['max_running_time'].strip()
    job_name = request.form['job_name'].strip()
    operation_type = request.form['operation_type'].strip()
    old_name = request.form['old_name'].strip()

    # [END submitted]

    # [START render_template]
    return render_template(
        'job.html',
        emails=emails,
        project_id=project_id,
        bucket_id=bucket_id,
        machine_name=machine_name,
        startup_script=startup_script,
        shutdown_script=shutdown_script,
        machine_type=machine_type,
        machine_zone=machine_zone,
        after_run=after_run,
        machine_os=machine_os,
        cron_schedule=cron_schedule,
        max_running_time=max_running_time,
        job_name = job_name,
        operation_type=operation_type,
        old_name=old_name
    )
    # [END render_template]


# View a job information
@app.route('/view_job', methods=['GET'])
def view_job():
    job_name = request.args.get('job_name')

    logging.info("view_job: Viewing job " + job_name)

    query_result = app_utils.get_job_by_name(job_name)
    existing_job = query_result[0]

    # If job exist redirect user to update job page with alert
    if len(query_result) > 0:
        return render_template(
            'view.html',
            emails=existing_job.emails,
            project_id=existing_job.project_id,
            bucket_id=existing_job.bucket_id,
            machine_name=existing_job.machine_name,
            startup_script=existing_job.startup_script,
            shutdown_script=existing_job.shutdown_script,
            machine_type=existing_job.machine_type,
            machine_zone=existing_job.machine_zone,
            after_run=existing_job.after_run,
            machine_os=existing_job.machine_os,
            cron_schedule=existing_job.cron_schedule,
            max_running_time=existing_job.max_running_time,
            job_name=existing_job.job_name

        )


# Create a job
@app.route('/modify_job_info', methods=['GET'])
def modify_job_info():
    logging.info("Run modify_info at > %s" % time.strftime("%c"))
    emails = request.args.get('emails').strip()
    project_id = request.args.get('project_id').strip()
    bucket_id = request.args.get('bucket_id').strip()
    machine_name = request.args.get('machine_name').strip()
    startup_script = request.args.get('startup_script').strip()
    shutdown_script = request.args.get('shutdown_script').strip()
    machine_type = request.args.get('machine_type').strip()
    machine_zone = request.args.get('machine_zone').strip()
    after_run = request.args.get('after_run').strip()
    machine_os = request.args.get('machine_os').strip()
    cron_schedule = request.args.get('cron_schedule').strip()
    max_running_time = request.args.get('max_running_time').strip()
    job_name = request.args.get('job_name').strip()
    alert_type = request.args.get('alert_type').strip()
    alert_message = request.args.get('alert_message').strip()
    operation_type = request.args.get('operation_type').strip()
    old_name = request.args.get('old_name').strip()

    return render_template(
        'form.html',
        emails_value=emails,
        project_id_value=project_id,
        bucket_id_value=bucket_id,
        machine_name_value=machine_name,
        startup_script_value=startup_script,
        shutdown_script_value = shutdown_script,
        machine_type_value=machine_type,
        machine_zone_value=machine_zone,
        after_run_value=after_run,
        machine_os_value=machine_os,
        cron_schedule_value=cron_schedule,
        max_running_time_value=max_running_time,
        job_name_value=job_name,
        alert_type=alert_type,
        alert_message=alert_message,
        operation="Modify job",
        operation_type=operation_type,
        old_name=old_name

    )

# List a jobs
@app.route('/list_job', methods=['GET'])
def list_job():
    logging.info("Run list_job at > %s" % time.strftime("%c"))

    jobs = app_utils.get_job_list()

    formated_jobs = []

    if len(jobs) > 0:
        # Convert cron to readable before listing values
        for job in jobs:

            # Intialize template
            job_entity = {
                "creation":"",
                "updated": "",
                "project_id": "",
                "machine_name": "",
                "machine_type": "",
                "machine_zone": "",
                "cron_schedule": "",
                "after_run": "",
                "max_running_time": "",
                "job_name": "",
                "last_run": "",
                "run_unit_cost": "",
                "job_status":"",
                "startup_script": "",
                "shutdown_script": ""
            }

            # Get db values
            creation = job.creation
            updated = job.updated
            project_id = job.project_id
            machine_name = job.machine_name
            machine_type = job.machine_type
            machine_zone = job.machine_zone
            cron_schedule = job.cron_schedule
            after_run = job.after_run
            max_running_time = job.max_running_time
            job_name = job.job_name
            job_status = job.job_status
            last_run = job.last_run
            startup_script=job.startup_script
            shutdown_script = job.shutdown_script

            # Create new entity with modified and calculated values
            job_entity['creation']=creation
            job_entity['updated'] = updated
            job_entity['machine_type'] = machine_type
            job_entity['project_id'] = project_id
            job_entity['machine_zone'] = machine_zone
            job_entity['max_running_time'] = max_running_time + 'min'
            job_entity['after_run'] = after_run
            job_entity['job_name'] = job_name
            job_entity['last_run'] = last_run
            job_entity['startup_script'] = startup_script
            job_entity['shutdown_script'] = shutdown_script
            job_entity['machine_name'] = machine_name


            # Readable cron
            job_entity['cron_schedule'] = app_utils.readable_cron(cron_schedule)

            # Check if instance is running for every job
            status = app_utils.instance_status(machine_name, project_id, job_status)


            # Get estimate pricing
            job_entity['run_unit_cost'] = app_utils.formated_estimate_running_cost(machine_type, max_running_time)

            # Chek job + instance status
            if status != None:
                job_entity['job_status']=status
            else:
                job_entity['job_status'] =job_status

            formated_jobs.append(job_entity)

    if len(jobs)>0:
        return render_template('list.html', jobs=formated_jobs)
    else:
        return redirect(url_for('form_job'))

# Create a job
@app.route('/create_job', methods=['POST'])
def create_job():
    logging.info("Run created_job at > %s" % time.strftime("%c"))
    # Get job configs
    emails = request.form['emails'].strip()
    project_id = request.form['project_id'].strip()
    bucket_id = request.form['bucket_id'].strip()
    machine_name = request.form['machine_name'].strip()
    startup_script = request.form['startup_script'].strip()
    shutdown_script = request.form['shutdown_script'].strip()
    machine_type = request.form['machine_type'].strip()
    machine_zone = request.form['machine_zone'].strip()
    after_run = request.form['after_run'].strip()
    machine_os = request.form['machine_os'].strip()
    cron_schedule = request.form['cron_schedule'].strip()
    max_running_time = request.form['max_running_time'].strip()
    job_name = request.form['job_name'].strip()
    operation_type = request.form['operation_type'].strip()
    old_name = request.form['old_name'].strip()


    if operation_type == "None":

        # Check if job exist

        existing_job=app_utils.get_job_by_name(job_name)

        logging.info("create_job: Saving new job "+request.form['job_name']+" to datastore ...")

        is_valid_conf = app_utils.is_job_config_valid(emails, cron_schedule, max_running_time)

        # If job exist redirect user to update job page with alert
        if len(existing_job) > 0 or is_valid_conf!="":

            if existing_job[0].job_name == request.form['job_name']:

                alert_type ="errorDialog"

                if len(existing_job) > 0:
                    alert_message="Job already exist with the same name " +existing_job[0].job_name
                    logging.info("Job already exist with the same name  " + request.form['job_name'] + " in datastore ...")
                else:
                    alert_message = "Cron value is not valid, please correct the value."
                    logging.info("Cron value ("+cron_schedule+") is not valid, please correct the value.")

                operation_type="correct_before_insert"
                old_name="None"

                return redirect(url_for('modify_job_info',emails=emails, project_id=project_id, bucket_id=bucket_id,
                              machine_name=app_utils.valid_instance_name(machine_name), startup_script=startup_script,
                             shutdown_script=shutdown_script,machine_type=machine_type,machine_zone=machine_zone,
                             after_run=after_run,machine_os=machine_os,cron_schedule=cron_schedule,max_running_time=max_running_time,
                             job_name=job_name,alert_type=alert_type,alert_message=alert_message, operation_type=operation_type,
                             old_name=old_name))

        else:

            if is_valid_conf=="":
                result = app_utils.create_job(emails, project_id, bucket_id, machine_type,
                       machine_name, startup_script, shutdown_script, machine_zone, after_run,
                       machine_os, cron_schedule, max_running_time, job_name)
            else:
                alert_type = "errorDialog"
                alert_message = is_valid_conf
                operation_type="correct_before_insert"
                old_name="None"
                logging.info(is_valid_conf)

                return redirect(url_for('modify_job_info',emails=emails, project_id=project_id, bucket_id=bucket_id,
                              machine_name=app_utils.valid_instance_name(machine_name), startup_script=startup_script,
                              shutdown_script=shutdown_script,machine_type=machine_type,machine_zone=machine_zone,
                              after_run=after_run,machine_os=machine_os,cron_schedule=cron_schedule,max_running_time=max_running_time,
                              job_name=job_name,alert_type=alert_type,alert_message=alert_message, operation_type=operation_type,
                             old_name=old_name))

            #TODO: Operation if insert isn't correct
            return redirect(url_for('list_job'))
    else:

        # Check if job exist
        last_run=None
        result = app_utils.update_job(job_name,emails, project_id, bucket_id, machine_type,
                   machine_name, startup_script, shutdown_script, machine_zone, after_run,
                   machine_os, cron_schedule, max_running_time, job_name, last_run)

        if not result:
            logging.info("Unable to update job " + old_name + ", job not found ...")

        return redirect(url_for('list_job'))


# Modify a jobs
@app.route('/update_job', methods=['POST'])
def update_job():
    logging.info("Run update_job at > %s" % time.strftime("%c"))
    job_name = request.form['job_name']

    #Get job
    """
    my_filter = "WHERE job_name='"+job_name+"'"
    my_job = job.Job().get(my_filter)
    """

    my_job = app_utils.get_job_by_name(job_name)

    if len(my_job) > 0:
        logging.info("Job already exist with the same name  " + request.form['job_name'] + " in datastore ...")

        alert_type    = "updating"
        alert_message = "Updating job " + my_job[0].job_name
        operation_type= "update"

        return redirect(url_for('modify_job_info', emails=my_job[0].emails, project_id=my_job[0].project_id,
                                bucket_id=my_job[0].bucket_id,machine_name=app_utils.valid_instance_name(my_job[0].machine_name),
                                shutdown_script=my_job[0].shutdown_script, startup_script=my_job[0].startup_script,machine_type=my_job[0].machine_type,
                                machine_zone=my_job[0].machine_zone, after_run=my_job[0].after_run,machine_os=my_job[0].machine_os,
                                cron_schedule=my_job[0].cron_schedule, max_running_time=my_job[0].max_running_time,
                                job_name=my_job[0].job_name,alert_type=alert_type, alert_message=alert_message,
                                operation_type=operation_type,old_name=my_job[0].job_name))
    else:
        # Redirect to list
        return redirect(url_for('list_job'))


# Modify a jobs
@app.route('/delete_job', methods=['POST'])
def delete_job():
    logging.info("Run delete_job at > %s" % time.strftime("%c"))
    job_name = request.form['job_name']

    #Get job
    """
    my_filter = "WHERE job_name='"+job_name+"'"
    my_job = job.Job().get(my_filter)
    """
    job = app_utils.get_job_by_name(job_name)

    if job[0].job_status == "running":
        # Make action to stop the instance
        logging.info("Job is running, stopping GCE instance ....")

    #Delete job
    result = app_utils.delete_job(job)
    #TODO: what tot do if job is not deleted
    # Redirect to list
    return redirect(url_for('list_job'))


# Run jobs
@app.route('/run_job', methods=['POST'])
def run_job():
    logging.info("Run run_job at > %s" % time.strftime("%c"))
    job_name = request.form['job_name']

    app_utils.run(job_name)

    # Redirect to list
    return redirect(url_for('list_job'))

# Stop jobs
@app.route('/stop_job', methods=['POST'])
def stop_job():
    logging.info("Run stop_job at > %s" % time.strftime("%c"))
    job_name = request.form['job_name']

    app_utils.stop(job_name)

    # Redirect to list
    return redirect(url_for('list_job'))

# Watch jobs
@app.route('/overwatch', methods=['GET'])
def overwatch():

    logging.info("Run watch_job at > %s" % time.strftime("%c"))

    app_utils.overwatch()

    return ""

# If error
@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.info("Run server_error at > %s" % time.strftime("%c"))
    logging.exception('An error occurred during a request. \n' + str(e))
    return redirect(url_for('list_job'))