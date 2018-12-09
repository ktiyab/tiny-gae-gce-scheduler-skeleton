# Tiny Google Cloud Platform Jobs Scheduler

## Introduction 

Warning: This is an POC which will be ameliorate

TGJS is a tiny GCP interfaced tool designed to help for reducing  costs of jobs planning in GCP in order to make the use of GCP more profitable for small business, even if he is already in some way.

For now some of solutions given by Google on GCP can be expensive or are not optimized by integrating easy use of combination of free services. This tool aim to help staying in the free tier usage of GCP,  as describe on this link: https://cloud.google.com/free/docs/always-free-usage-limits

At December 2018, below are the free usage limits of GCP services included in TGJS

##### App Engine free usage limits

- 28 frontend instance hours per day, 9 backend instance hours per day
- 5 GB Cloud Storage
- 1 GB of egress per day
- Shared memcache
- 1000 search operations per day, 10 MB search indexing
- 100 emails per day
- The free tier is available only for the Standard Environment.

##### Cloud Datastore

- 1 GB storage
- 50,000 reads, 20,000 writes, 20,000 deletes

##### Compute Engine

- 1 non-preemptible f1-micro VM instance per month in one of the following US regions:
    - Oregon: us-west1
    - Iowa: us-central1
    - South Carolina: us-east1
- 30 GB-months HDD, 5 GB-months snapshot
- 1 GB network egress from North America to all region destinations per month (excluding China and Australia)

Your Always Free f1-micro instance limit is by time, not by instance. Eligible use of all of your f1-micro instances each month is free until you have used a number of hours equal to the total hours in the current month.Usage calculations are combined across the supported regions.

##### Cloud Storage

- 5 GB-months of Regional Storage (US regions only)
- 5000 Class A Operations per month
- 50000 Class B Operations per month
- 1 GB network egress from North America to all region destinations per month (excluding China and Australia)

Always Free only available in us-east1, us-west1, and us-central1 regions. Usage calculations are combined across those regions.

##### For intensive jobs 

You can use this tool if you want to run a quick job on Google Compute Engine by scheduleding it. But for extensive use of Compute Engine this solution may not be th best choice than other solutions provided natively by Google, you can use the cloud architectures proposed by Google to manage that kind of job. Some example below:
- Reliable Task Scheduling on Google Compute Engine: https://cloud.google.com/solutions/reliable-task-scheduling-compute-engine
- 



## Presentation 

TGJS is based on Google App Engine (GAE), Google Datastore (GD), Google Compute Engine (GCE) and Google Cloud Storage (GCS).

TGJS run on a tiny instance of GAE, with his interface you can schedule a jobs which are saved in Datastore. 

GAE crontab run by default every 1 min and  then read jobs list scheduled in Datastore, create job queues wich can automatically create GCE instances. 

TGJS with GCE can run your scripts from GCS on startup. When instances are shutdown  TGJS stop or delete the GCE instance after an elapsed time indicated by you.

### 1 - Checkout the code skeleton

This code skeleton aimed to help you to quicly setup a GCE scheduler for your GCP jobs.

### 2 - Add your GCP service account and install librairies

Add Google Cloud Service Acount json key file in the credentials folder, the json file must be named as the GCP project related.

Install requirement libraries by executing command below:

```
$  pip install -t lib -r requirements.txt
```

This command will install required librairies on lib folder.

### 3 - Run app engine locally and test

#### Run Google App Engine locally

##### Install Google Cloud SDK and toos

To run GAE on local for tests purpose you must install some Google Cloud Packages by executing command below:

```
$ sudo apt-get update && sudo apt-get install google-cloud-sdk &&  $ sudo apt-get install google-cloud-sdk-app-engine-python google-cloud-sdk-datastore-emulator 
```

##### Configure Google App Engine YAML files at your convenience

You can configure GAE Yaml file as your convenience to increase or decrease instance CPU, RAM, Crontab or autoamtique scaling.

##### Run Google App Engine locally

You can execute command bellow in the root folder to run the web app:

```
$ dev_appserver.py app.yaml 
```

In dev mode, local crontab doesn't work, you can run the local_dev_cron.py to simulate local crontab for test purpose.






