import googleapiclient.discovery
import logging, requests
import time
from json import dumps
from subprocess import call
from google.cloud import bigquery

def retrain():
    # TODO: Delete entities from Datastore
    # TODO: Export BigQuery table to Cloud Storage Bucket
    # TODO: Concatenate csv with existing training data
    # TODO: Retrain

    ### EXPORT BATCH TRAINING DATA FROM DATASTORE TO CLOUD STORAGE BUCKET ###
    GOOGLE_APPLICATION_CREDENTIALS='cafe-app-f9f9134f1cd3.json'
    TOKEN='ya29.Gl27BZ2iqGHqdYGgZwm8Z8oHhqAjnM-RFclb4jpdWckxULQDsjOdz3mfBOv2GgqkQSV6nKnbpe-40o0bmtGQp2bvJUpE6aAQ9Vc2eizJdjmOoIqakKRZrg-0mFu4LXA'

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
    print("responseDSData = ")
    print(responseDSData)

    ### LOAD METADATA FROM CLOUD STORAGE BUCKET TO BIGQUERY ###
    big_query_service_acct = "cafe-app-54e9e8e2ce3e.json"
    
    outputUrlPrefix = responseDSData["metadata"]["outputUrlPrefix"]
    exportedDataPath = str(outputUrlPrefix + "/default_namespace/kind_Wait/default_namespace_kind_Wait.export_metadata")

    print("exportedDataPath = " + exportedDataPath)

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
          "writeDisposition": "WRITE_TRUNCATE",
          "schema": {
            "fields" : [
                "duration"
            ]
          }
        }
      },
      "jobReference": {
        "location": "US"
      }
    }
    bodyBQ = dumps(requestBodyBQ)

    time.sleep(10)

    responseBQ = requests.post("https://www.googleapis.com/bigquery/v2/projects/cafe-app-200914/jobs",
        data=str(bodyBQ),
        headers={
            "Authorization":"Bearer " + TOKEN,
            "Content-Type":"application/json"}
        )
    print(responseBQ.status_code, responseBQ.reason, responseBQ.text)
    responseBQData = responseBQ.json()
    print("responseBQData = ")
    print(responseBQData)

    time.sleep(50)

    ### EXPORT BIGQUERY TABLE TO CLOUD STORAGE BUCKET AS CSV ###
    client = bigquery.Client()
    bucket_name = "cafe-app-200914-mlengine"
    project = "cafe-app-200914"
    dataset_id = 'training'
    table_id = 'batch'

    destination_uri = 'gs://{}/{}'.format(bucket_name, '/data/batch.csv')
    dataset_ref = client.dataset(dataset_id, project=project)
    table_ref = dataset_ref.table(table_id)

    extract_job = client.extract_table(
        table_ref,
        destination_uri)  # API request
    extract_job.result()  # Waits for job to complete.

    print('Exported {}:{}.{} to {}'.format(
        project, dataset_id, table_id, destination_uri))


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
