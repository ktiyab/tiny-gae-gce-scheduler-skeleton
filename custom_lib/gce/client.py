"""
Copyright Tiyab KONLAMBIGUE

Licensed under the BSD 3-Clause "New" or "Revised" license;
you may not use this file except in compliance with the License.
You may obtain a copy of the License at : https://opensource.org/licenses/BSD-3-Clause
"""
import sys
import time
import json
import googleapiclient.http
from googleapiclient.discovery import build, DISCOVERY_URI
from io import StringIO
from httplib2 import Http

"""
from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build
from six.moves import input
"""

#gcloud compute images list
GCE_DEFAULT_IMAGE_PROJECT = "ubuntu-os-cloud"

GCE_DEFAULT_IMAGE_NAME    = "ubuntu-1804-bionic-v20181120"

#gcloud compute machine-types list
GCE_DEFAULT_MACHINE_TYPE = "n1-standard-1"


GCE_DEFAULT_FULL_SCOPE=[
                'https://www.googleapis.com/auth/compute',
                'https://www.googleapis.com/auth/bigquery',
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]

#gcloud compute zones list
GCE_DEFAULT_ZONE ="europe-west1-b"

def get_client(project_id=None, credentials=None,
               service_url=None, service_account=None,
               private_key=None, private_key_file=None,
               json_key=None, json_key_file=None,
               readonly=True, swallow_results=True,
               num_retries=0):
    """Return a singleton instance of Compute Engine Client. Either
    AssertionCredentials or a service account and private key combination need
    to be provided in order to authenticate requests to Compute Engine .

    Parameters
    ----------
    project_id : str, optional
        The Compute Engine  project id, required unless json_key or json_key_file is
        provided.
    credentials : oauth2client.client.SignedJwtAssertionCredentials, optional
        AssertionCredentials instance to authenticate requests to Compute Engine
        (optional, must provide `service_account` and (`private_key` or
        `private_key_file`) or (`json_key` or `json_key_file`) if not included
    service_url : str, optional
        A URI string template pointing to the location of Google's API
        discovery service. Requires two parameters {api} and {apiVersion} that
        when filled in produce an absolute URI to the discovery document for
        that service. If not set then the default googleapiclient discovery URI
        is used. See `credentials`
    service_account : str, optional
        The Google API service account name. See `credentials`
    private_key : str, optional
        The private key associated with the service account in PKCS12 or PEM
        format. See `credentials`
    private_key_file : str, optional
        The name of the file containing the private key associated with the
        service account in PKCS12 or PEM format. See `credentials`
    json_key : dict, optional
        The JSON key associated with the service account. See `credentials`
    json_key_file : str, optional
        The name of the JSON key file associated with the service account. See
        `credentials`.
    readonly : bool
        Bool indicating if Compute Engine  access is read-only. Has no effect if
        credentials are provided. Default True.
    swallow_results : bool
        If set to False, then return the actual response value instead of
        converting to boolean. Default True.
    num_retries : int, optional
        The number of times to retry the request. Default 0 (no retry).


    Returns
    -------
    Compute Engine Client
        An instance of the Compute Engine client.
    """

    if not credentials:
        assert (service_account and (private_key or private_key_file)) or (
                json_key or json_key_file), \
            'Must provide AssertionCredentials or service account and P12 key\
            or JSON key'

    if not project_id:
        assert json_key or json_key_file, \
            'Must provide project_id unless json_key or json_key_file is\
            provided'

    if service_url is None:
        service_url = DISCOVERY_URI

    scope = GCE_DEFAULT_FULL_SCOPE

    if private_key_file:
        credentials = _credentials().from_p12_keyfile(service_account,
                                                      private_key_file,
                                                      scopes=scope)

    if private_key:
        try:
            if isinstance(private_key, basestring):
                private_key = private_key.decode('utf-8')
        except NameError:
            # python3 -- private_key is already unicode
            pass
        credentials = _credentials().from_p12_keyfile_buffer(
            service_account,
            StringIO(private_key),
            scopes=scope)

    if json_key_file:
        with open(json_key_file, 'r') as key_file:
            json_key = json.load(key_file)

    if json_key:
        credentials = _credentials().from_json_keyfile_dict(json_key,
                                                            scopes=scope)
        if not project_id:
            project_id = json_key['project_id']

    gce_service = _get_gce_service(credentials=credentials,
                                 service_url=service_url)

    return ComputeEngineClient(gce_service, project_id)

#### Create Google Compute Engine credential
def _get_gce_service(credentials=None, service_url=None):
    """Construct an authorized Compute engine service object."""

    assert credentials, 'Must provide ServiceAccountCredentials'

    http = credentials.authorize(Http())
    service = build(
        'compute',
        'v1',
        http=http,
        discoveryServiceUrl=service_url,
        cache_discovery=False
    )

    return service

def _credentials():
    """Import and return SignedJwtAssertionCredentials class"""
    from oauth2client.service_account import ServiceAccountCredentials

    return ServiceAccountCredentials


class ComputeEngineClient(object):

    def __init__(self, gce_service, project_id):
        self.compute_engine = gce_service
        self.project_id =project_id

        #Script name on default bucket in project with project_name
        #self.startup_scrip_name =startup_scrip_name


    # [START list_instances]
    def list_instances(self, project,
                       zone=GCE_DEFAULT_ZONE):
        compute = self.compute_engine

        result = compute.instances().list(project=project, zone=zone).execute()
        return result['items']
    # [END list_instances]


    # [START create_instance]
    def create_instance(self,
                        project_id,
                        machine_name,
                        gcs_startup_script,
                        bucket_id,
                        zone=GCE_DEFAULT_ZONE,
                        image_project=GCE_DEFAULT_IMAGE_PROJECT,
                        image_name=GCE_DEFAULT_IMAGE_NAME,
                        type_machine=GCE_DEFAULT_MACHINE_TYPE
                        ):

        compute = self.compute_engine

        ## The pattern here is: "projects/${PROJECT}/global/images/${IMAGE}"
        # gcloud compute images list
        source_disk_image = "projects/%s/global/images/%s" % (image_project, image_name)

        #gcloud compute machine-types list
        machine_type = "zones/%s/machineTypes/%s" % (zone, type_machine)

        #startup_script = open(startup_scrip_name, 'r').read()

        config = {
            'name': machine_name,
            'machineType': machine_type,

            # Specify the boot disk and the image to use as a source.
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': source_disk_image,
                    }
                }
            ],

            # Specify a network interface with NAT to access the public
            # internet.
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],

            # Allow the instance to access cloud storage and logging.
            'serviceAccounts': [{
                'email': 'default',
                'scopes': GCE_DEFAULT_FULL_SCOPE
            }],

            # Metadata is readable from the instance and allows you to
            # pass configuration from deployment scripts to instances.
            'metadata': {
                'items': [{
                    # Startup script is automatically executed by the
                    # instance upon startup.
                    'key': 'startup-script-url',
                    'value': gcs_startup_script
                },
                {
                    # Every project has a default Cloud Storage bucket that's
                    # the same name as the project.
                    'key': 'bucket',
                    'value': bucket_id
                }]
            }
        }

        try:
            operation = compute.instances().insert(
                project=project_id,
                zone=zone,
                body=config).execute()

            #Wait for instance creation
            self.wait_for_operation(project_id, operation['name'])


        except Exception as e:
            #If problem occured,delete the instance
            print("Unable to create the instance " + machine_name + " we have error: " + str(e))
            print("\n Trying to remove the instance if create")
            try:
                self.delete_instance(project_id, machine_name, zone)
            finally:
                print("...")
    # [END create_instance]


    # [START delete_instance]
    def delete_instance(self, project,
                        name,
                        zone=GCE_DEFAULT_ZONE):

        compute = self.compute_engine

        return compute.instances().delete(
            project=project,
            zone=zone,
            instance=name).execute()
    # [END delete_instance]


    # [START stop_instance]
    def stop_instance(self, project,
                        name,
                        zone=GCE_DEFAULT_ZONE):

        compute = self.compute_engine

        operation = compute.instances().stop(
            project=project,
            zone=zone,
            instance=name).execute()


        # Wait for instance creation
        self.wait_for_operation(project, operation['name'])
    # [END stop_instance]


    # [START start_instance]
    def start_instance(self, project,
                        name,
                        zone=GCE_DEFAULT_ZONE):

        compute = self.compute_engine

        operation = compute.instances().start(
            project=project,
            zone=zone,
            instance=name).execute()

        # Wait for instance creation
        self.wait_for_operation(project, operation['name'])

    # [END start_instance]


    # [START wait_for_operation]
    def wait_for_operation(self, project,
                           operation,
                           zone=GCE_DEFAULT_ZONE):

        compute = self.compute_engine

        sys.stdout.write('\nWaiting for operation to finish...')
        while True:
            result = compute.zoneOperations().get(
                project=project,
                zone=zone,
                operation=operation).execute()

            if result['status'] == 'DONE':
                print(">> DONE.")
                if 'error' in result:
                    raise Exception(result['error'])
                return result
            else:
                print("\n>> Job state is " + result['status'])
                time.sleep(10)
    # [END wait_for_operation]