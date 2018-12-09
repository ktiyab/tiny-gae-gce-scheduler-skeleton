"""
Copyright Tiyab KONLAMBIGUE

Licensed under the BSD 3-Clause "New" or "Revised" license;
you may not use this file except in compliance with the License.
You may obtain a copy of the License at : https://opensource.org/licenses/BSD-3-Clause
"""
from google.appengine.ext import ndb

class Job(ndb.Model):

    creation         = ndb.DateTimeProperty(auto_now_add=True)
    updated          = ndb.DateTimeProperty(auto_now=True)
    emails           = ndb.StringProperty()
    project_id       = ndb.StringProperty()
    bucket_id        = ndb.StringProperty()
    machine_name     = ndb.StringProperty()
    startup_script   = ndb.StringProperty()
    shutdown_script  = ndb.StringProperty()
    machine_type     = ndb.StringProperty()
    machine_zone     = ndb.StringProperty()
    machine_os       = ndb.StringProperty()
    cron_schedule    = ndb.StringProperty()
    after_run        = ndb.StringProperty()
    max_running_time = ndb.StringProperty()
    job_name         = ndb.StringProperty()
    job_status       = ndb.StringProperty()
    last_run         = ndb.DateTimeProperty()

    # Get list of job
    @classmethod
    def query(self, query, max_line):
        results = []

        query = ndb.GqlQuery(query)

        for query_line in query.run(limit=max_line):
            results.append(query_line)
        return  results

    # Get job
    def get(self, filtering):

        results = []

        query = self.gql(filtering)

        for query_line in query:
            results.append(query_line)
        return  results

    def to_dict(self):

        return {
            "key": self.key.urlsafe() if self.key else None,
            "creation": str(self.creation) if self.creation else None,
            "updated": str(self.updated) if self.updated else None,
            "emails": str(self.emails) if self.emails else None,
            "project": str(self.project) if self.project else None,
            "bucket_id": str(self.bucket_id) if self.bucket_id else None,
            "machine_name": str(self.machine_name) if self.machine_name else None,
            "startup_script": str(self.startup_script) if self.startup_script else None,
            "shutdown_script": str(self.shutdown_script) if self.shutdown_script else None,
            "machine_type": str(self.machine_type) if self.machine_type else None,
            "machine_zone": str(self.machine_zone) if self.machine_zone else None,
            "machine_os": str(self.machine_os) if self.machine_os else None,
            "after_run": str(self.after_run) if self.after_run else None,
            "cron_schedule": str(self.cron_schedule) if self.cron_schedule else None,
            "max_running_time": str(self.max_running_time) if self.max_running_time else None,
            "job_name": str(self.job_name) if self.job_name else None,
            "job_status": str(self.job_status) if self.job_status else None,
            "last_run": str(self.last_run) if self.last_run else None,
        }


## JOB TO RUN QUEUE
class Queue(ndb.Model):

    creation         = ndb.DateTimeProperty(auto_now_add=True)
    project_id       = ndb.StringProperty()
    bucket_id        = ndb.StringProperty()
    machine_name     = ndb.StringProperty()
    machine_type     = ndb.StringProperty()
    machine_zone     = ndb.StringProperty()
    machine_os       = ndb.StringProperty()
    after_run        = ndb.StringProperty()
    max_running_time = ndb.StringProperty()
    job_name         = ndb.StringProperty()

    # Get list of job
    @classmethod
    def query(self, query, max_line):
        results = []

        query = ndb.GqlQuery(query)

        for query_line in query.run(limit=max_line):
            results.append(query_line)
        return  results

    # Get job
    def get(self, filtering):

        results = []

        query = self.gql(filtering)

        for query_line in query:
            results.append(query_line)
        return  results

    def to_dict(self):

        return {
            "key": self.key.urlsafe() if self.key else None,
            "creation": str(self.creation) if self.creation else None,
            "project": str(self.project) if self.project else None,
            "bucket_id": str(self.bucket_id) if self.bucket_id else None,
            "machine_name": str(self.machine_name) if self.machine_name else None,
            "machine_type": str(self.machine_type) if self.machine_type else None,
            "machine_zone": str(self.machine_zone) if self.machine_zone else None,
            "machine_os": str(self.machine_os) if self.machine_os else None,
            "after_run": str(self.after_run) if self.after_run else None,
            "max_running_time": str(self.max_running_time) if self.max_running_time else None,
            "job_name": str(self.job_name) if self.job_name else None,
            "job_status": str(self.job_status) if self.job_status else None,
        }
