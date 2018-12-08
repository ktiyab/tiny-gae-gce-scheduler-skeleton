# tiny-gae-gce-scheduler-skeleton

Warning: This is an POC wich will be ameliorate

T2GSK is a tiny GAE scheduler with purpose to reduce cost of scheduling jobs in GCP.

T2GSK is based on Google App Engine (GAE), Google Datastore (GD) and Google Compute Engine (GCE).

T2GSK run on a tiny instance of GAE, with the interface you can schedule a jobs
wich are saved in Datastore. GAE crontab run by default every 1 min and read jobs 
scheduled in Datastore and create automatically GCE instance, run your script and stop
or delete the GCE instance after run.
