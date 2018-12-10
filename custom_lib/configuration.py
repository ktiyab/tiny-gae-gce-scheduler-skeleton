MIN_TIME_TO_RUN = 1
SLEEP_TIME_AFTER_DATASTORE_OP = 2
SLEEP_TIME_AFTER_GCE_OP = 2

JSON_KEY_FOLDER = "./credentials/"

# You can obtain the list by running: $ gcloud compute images list
GCE_DEFAULT_IMAGE_PROJECT = "ubuntu-os-cloud"

GCE_DEFAULT_IMAGE_NAME    = "ubuntu-1804-bionic-v20181120"

# You can obtain the list by running: $ gcloud compute machine-types list
GCE_DEFAULT_MACHINE_TYPE = "n1-standard-1"

# Google cloud scope list: https://developers.google.com/identity/protocols/googlescopes
GCE_DEFAULT_FULL_SCOPE=[
                'https://www.googleapis.com/auth/compute',
                'https://www.googleapis.com/auth/bigquery',
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]

# You can obtain the list by running: $ gcloud compute zones list
GCE_DEFAULT_ZONE ="europe-west1-b"

# Estimated hourly pricing at 2018/12 https://cloud.google.com/compute/pricing
GCE_PRICING = {
    "f1-micro":"0.0076",
    "g1-small":"0.0257",
    "n1-highcpu-8":"0.2836",
    "n1-highmem-2":"0.1184"
}
GCE_PRICING_CURRENCY = "$"


# More minute add to wait before stopping or deleting instance
MAX_GRACE_MIN = 5


# Google instance image project configs
IMAGES_PROJECT = [
    {
    "key-word": "ubuntu",
    "image-project" : "ubuntu-os-cloud"
    }
]