# Tiny Google Cloud Platform Jobs Scheduler

Warning: This is an POC which will be ameliorate

TGJS is a tiny GCP scheduler aimed to reduce cost of scheduling jobs in GCP.

TGJS is based on Google App Engine (GAE), Google Datastore (GD), Google Compute Engine (GCE) and Google Cloud Storage.

TGJS run on a tiny instance of GAE, with his interface you can schedule a jobs which are saved in Datastore. 

GAE crontab run by default every 1 min and read jobs list scheduled in Datastore and create job queues wich are automatically create GCE instances. TGJS with GCE can run your scripts from GCS on startup and when instances are shutdown  then stop or delete the GCE instance after an elapsed time indicated by you.


## 1 - Checkout the code skeleton

This code skeleton aimed to help you to quicly setup a GCE scheduler for your GCP jobs.

## 2 - Add your GCP service account and install librairies

Add Google Cloud Service Acount json key file in the credentials folder, the json file must be named as the GCP project related.

Install requirement libraries by executing command below:

```
$  pip install -t lib -r requirements.txt
```

This command will install required librairies on lib folder.

## 3 - Run app engine locally and test

### Run Google App Engine locally

#### Install Google Cloud SDK and toos

To run GAE on local for tests purpose you must install some Google Cloud Packages by executing command below:

```
$ sudo apt-get update && sudo apt-get install google-cloud-sdk &&  $ sudo apt-get install google-cloud-sdk-app-engine-python google-cloud-sdk-datastore-emulator 
```

#### Configure Google App Engine YAML files at your convenience

You can configure GAE Yaml file as your convenience to increase or decrease instance CPU, RAM, Crontab or autoamtique scaling.

#### Run Google App Engine locally

You can execute command bellow in the root folder to run the web app:

```
$ dev_appserver.py app.yaml 
```

In dev mode, local crontab doesn't work, you can run the local_dev_cron.py to simulate local crontab for test purpose.






