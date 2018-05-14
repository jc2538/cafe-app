import googleapiclient.discovery
import logging, requests
# import aiohttp
# import asyncio
import time
from json import dumps
from subprocess import call
# from google_auth_oauthlib.flow import InstalledAppFlow

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

# async def fetch(session, url, json):
#     async with session.post(url, json=json) as response:
#         print("FETCH RESULT = ")
#         print(response)
#         return await response.json()

# async def request(url, body, headers):
#     async with aiohttp.ClientSession(headers=headers) as session:
#         response = await fetch(session, url, body)
#         return response

def retrain():
    # TODO: Export entities into a csv for the training batch
    # TODO: Delete entities from the datastore
    # TODO: Concatenate csv with existing training data
    # TODO: Retrain

    ### EXPORT BATCH TRAINING DATA FROM DATASTORE TO CLOUD STORAGE BUCKET ###
    GOOGLE_APPLICATION_CREDENTIALS='cafe-app-f9f9134f1cd3.json'
    TOKEN='ya29.Gl27BTP9cA5uu_AJRqncJJY9jpT5BBxtX59Vq-q4s_-VybTIf8jr07fmvXeQwH9giiuY10yfCJuAVievAWCTF6o2AgEPKgZcsBdXQxOZBLwHCgJp56Kdg-saWF7JOzc'

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
       
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # responseDSData = loop.run_until_complete(request(urlDS, requestBodyDS, headers))

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
          "writeDisposition": "WRITE_TRUNCATE" 
        }
      },
      "jobReference": {
        "location": "US"
      }
    }
    bodyBQ = dumps(requestBodyBQ)
    # print("requestBodyBQ = ")
    # print(requestBodyBQ)
    print("bodyBQ = ")
    print(bodyBQ)

    # responseBQData = loop.run_until_complete(request(urlBQ, requestBodyBQ, headers))

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
    # Create the ML Engine service object.
    # To authenticate set the environment variable
    # logging.basicConfig(filename='ml_model.log', level=logging.INFO)
    # logging.info('inside')
    # logging.info(project)
    # logging.info(model)
    # logging.info(instances)
    # logging.info(version)
    GOOGLE_APPLICATION_CREDENTIALS='cafe-app-f9f9134f1cd3.json'
    service = googleapiclient.discovery.build('ml', 'v1', cache_discovery=False)
    # logging.info('cred')
    name = 'projects/{}/models/{}'.format(project, model)
    # logging.info('name')

    if version is not None:
        name += '/versions/{}'.format(version)
    # logging.info('version')

    #instances = [{"location_id": 0, "hour": 7, "minute": 30, "total_minutes": 420}]
    # print("instances here")
    # print(instances)

    response = service.projects().predict(
        name=name,
        body={'instances': instances}
    ).execute()

    # print response

    if 'error' in response:
        return "error"
        raise RuntimeError(response['error'])

    return str(response['predictions'][0]['predictions'][0]) + " minutes"
