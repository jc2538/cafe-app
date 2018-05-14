import googleapiclient.discovery
import logging, requests
import time, datetime
from json import dumps
from subprocess import call
from google.cloud import bigquery

#Submits job
def retrain_helper():
    JOB_NAME = 'cafe_' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
    print(JOB_NAME)
    training_inputs = {'scaleTier': 'STANDARD_1',
        # 'masterType': 'complex_model_m',
        # 'workerType': 'complex_model_m',
        # 'parameterServerType': 'large_model',
        # 'workerCount': 9,
        # 'parameterServerCount': 3,
        'packageUris': ['gs://cafe-app-200914-mlengine/trainer-0.0.0.tar.gz'],
        'pythonModule': 'trainer.task',
        'args': ['--train-files', 'gs://cafe-app-200914-mlengine/data/training_data.csv', '--eval-files', 'gs://cafe-app-200914-mlengine/data/test_data.csv', "--train-steps", "1000", "--verbosity", "DEBUG", "--eval-steps", "100"],
        'region': 'us-central1',
        'jobDir': 'gs://cafe-app-200914-mlengine/' + JOB_NAME,
        'runtimeVersion': '1.4'}

    job_spec = {'jobId': JOB_NAME, 'trainingInput': training_inputs}

    project_name = 'cafe-app-200914'
    project_id = 'projects/{}'.format(project_name)
    cloudml = googleapiclient.discovery.build('ml', 'v1')

    request = cloudml.projects().jobs().create(body=job_spec,
                parent=project_id)
    # response = request.execute()

    try:
        response = request.execute()
        # You can put your code for handling success (if any) here.

    except HTTPError as err:
        # Do whatever error response is appropriate for your application.
        # For this example, just send some text to the logs.
        # You need to import logging for this to work.
        logging.error('There was an error creating the training job.'
                      ' Check the details:')
        logging.error(err._get_reason())
    
def retrain():
    # TODO: Delete entities from Datastore
    # TODO: Export BigQuery table to Cloud Storage Bucket
    # TODO: Concatenate csv with existing training data
    # TODO: Retrain

    ### EXPORT BATCH TRAINING DATA FROM DATASTORE TO CLOUD STORAGE BUCKET ###

    GOOGLE_APPLICATION_CREDENTIALS='cafe-app-f9f9134f1cd3.json'
    
    TOKEN='ya29.Gl27BcTuyVue5YD0Tadhtq6b2YpvJTrgDha4QDDcg4KofJLAc6INgodjC6BngcrurgXzN76KIcpbDjTyDFhnwT1DLzHaUb4I-anIxCle8unE3QzjhfxEjEUwZrBbb8k'

    headers={
        "Authorization":"Bearer " + TOKEN,
        "Content-Type":"application/json"
        }
    urlDS = "https://datastore.googleapis.com/v1beta1/projects/cafe-app-200914:export"
    requestBodyDS = {
        "entityFilter": {
            "kinds": ["Wait"],
            "namespaceIds": [""]
            },
        "outputUrlPrefix": "gs://cafe-app-datastore"
        }
        
    bodyDS = dumps(requestBodyDS)
       
    responseDS = requests.post("https://datastore.googleapis.com/v1beta1/projects/cafe-app-200914:export",
    data=str(bodyDS),
    headers={
        "Authorization":"Bearer " + TOKEN,
        "Content-Type":"application/json"}
    )

    responseDSData = responseDS.json()
    print("RESPONSEDSDATA = ")
    print(responseDSData)

    time.sleep(10)

    ### LOAD METADATA FROM CLOUD STORAGE BUCKET TO BIGQUERY ###

    big_query_service_acct = "cafe-app-54e9e8e2ce3e.json"
    
    outputUrlPrefix = responseDSData["metadata"]["outputUrlPrefix"]
    exportedDataPath = str(outputUrlPrefix + "/default_namespace/kind_Wait/default_namespace_kind_Wait.export_metadata")

    print("EXPORTEDDATAPATH = " + exportedDataPath)

    urlBQ = "https://www.googleapis.com/bigquery/v2/projects/cafe-app-200914/jobs"
    requestBodyBQ = {
      "configuration": {
        "load": {
          "sourceUris": [
            exportedDataPath
          ],
          "sourceFormat": "DATASTORE_BACKUP",
          "destinationTable": {
            "projectId": "cafe-app-200914",
            "datasetId": "training",
            "tableId": "batch"
          },
          "timePartitioning": {
            "type": "DAY"
          },
          "writeDisposition": "WRITE_TRUNCATE"
        }
      },
      "jobReference": {
        "location": "US"
      }
    }
    bodyBQ = dumps(requestBodyBQ)    

    responseBQ = requests.post("https://www.googleapis.com/bigquery/v2/projects/cafe-app-200914/jobs",
        data=str(bodyBQ),
        headers={
            "Authorization":"Bearer " + TOKEN,
            "Content-Type":"application/json"}
        )
    print(responseBQ.status_code, responseBQ.reason, responseBQ.text)
    responseBQData = responseBQ.json()
    print("RESPONSEBQDATA = ")
    print(responseBQData)

    time.sleep(10)

    ### CREATE NEW BQ TABLE WITHOUT NESTED FIELDS BY QUERYING ABOVE TABLE ###
   
    client = bigquery.Client()

    job_config = bigquery.QueryJobConfig()

    table_ref = client.dataset("training").table("batch3")
    job_config.destination = table_ref
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

    # Start the query, passing in the extra configuration.
    query =  (
        'SELECT location, publishedTime, duration '
        'FROM `training.batch`')
    query_job = client.query(
        query,
        location='US',
        job_config=job_config)  # API request - starts the query

    rows = list(query_job)  # Waits for the query to finish
    print("QUERY JOB FINISHED WITH 1ST ROW = " + str(rows[0]))
    # print(rows)

    ### EXPORT BIGQUERY TABLE TO CLOUD STORAGE BUCKET AS CSV ###
    
    bucket_name = "cafe-app-200914-mlengine"
    project = "cafe-app-200914"
    dataset_id = 'training'
    table_id = 'batch3' # TODO: Change this to the new table without nested fields

    destination_uri = 'gs://{}/{}'.format(bucket_name, '/data/batch3.csv')
    dataset_ref = client.dataset(dataset_id, project=project)
    table_ref = dataset_ref.table(table_id)

    extract_job = client.extract_table(
        table_ref,
        destination_uri)  # API request
    extract_job.result()  # Waits for job to complete.

    print('EXPORTED {}:{}.{} to {}'.format(
        project, dataset_id, table_id, destination_uri))

    retrain_helper()


def predict_json(project, model, instances, version=None):
    """Send json data to a deployed model for prediction.

    Args:
        project (str): project where the Cloud ML Engine Model is deployed.
        model (str): model name.
        instances ([Mapping[str: Any]]): Keys should be the names of Tensors
            your deployed model expects as inputs. Values should be datatypes
            convertible to Tensors, or (potentially nested) lists of datatypes
            convertible to tensors.
        version: str, version of the model to target.
    Returns:
        Mapping[str: any]: dictionary of prediction results defined by the
            model.
    """

    GOOGLE_APPLICATION_CREDENTIALS='cafe-app-f9f9134f1cd3.json'
    service = googleapiclient.discovery.build('ml', 'v1', cache_discovery=False)
    name = 'projects/{}/models/{}'.format(project, model)

    if version is not None:
        name += '/versions/{}'.format(version)

    response = service.projects().predict(
        name=name,
        body={'instances': instances}
    ).execute()

    if 'error' in response:
        return "error"
        raise RuntimeError(response['error'])

    return str(response['predictions'][0]['predictions'][0]) + " minutes"

# def get_token():
#     # CLIENT_ID = 795479451499-r06p1nlp3dgpiuhtba3pvblootc6afmv.apps.googleusercontent.com
#     # CLIENT_SECRET = Z2H7LsVOQN1gohstucRi9mRY
#     flow = InstalledAppFlow.from_client_secrets_file(
#         '/Users/jessicachen/Documents/College/CS5412/cafe-app/bookshelf/client_secret_795479451499-83ugvgq1giti1lusmufu1cnotf22v4mv.apps.googleusercontent.com.json',
#         scopes=['https://www.googleapis.com/auth/drive.metadata'])
#     credentials = flow.run_console()
#     print("credentials")
#     print(credentials)
#     print("end credentials")
#     return credentials 
