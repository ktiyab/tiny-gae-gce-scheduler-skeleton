# Tiny Google Cloud Platform Jobs Scheduler

Warning: This is an POC which will be ameliorate

TGJS is a tiny GCP scheduler aimed to reduce cost of scheduling jobs in GCP.

TGJS is based on Google App Engine (GAE), Google Datastore (GD), Google Compute Engine (GCE) and Google Cloud Storage.

TGJS run on a tiny instance of GAE, with his interface you can schedule a jobs which are saved in Datastore. 

GAE crontab run by default every 1 min and read jobs list scheduled in Datastore and create job queues wich are automatically create GCE instances. TGJS with GCE can run your scripts from GCS on startup and when instances are shutdown  then stop or delete the GCE instance after an elapsed time indicated by you.
