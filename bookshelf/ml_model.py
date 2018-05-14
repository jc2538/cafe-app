import googleapiclient.discovery
import logging, requests
import aiohttp
import asyncio
from json import dumps
from subprocess import call

async def fetch(session, url, json):
    async with session.post(url, json=json) as response:
        return await response.json()

async def request(url, body, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await fetch(session, url, body)
        return response

def retrain():
    # TODO: Export entities into a csv for the training batch
    # TODO: Delete entities from the datastore
    # TODO: Concatenate csv with existing training data
    # TODO: Retrain

    ### EXPORT BATCH TRAINING DATA FROM DATASTORE TO CLOUD STORAGE BUCKET ###
    GOOGLE_APPLICATION_CREDENTIALS='cafe-app-f9f9134f1cd3.json'

    headers={
        "Authorization":"Bearer ya29.Gl27BZbKv4v_DAhnBpddlJAroKlny_3FmJOF9TMYhYbHSyIbhU5Y1K2-37-Xb4DsA15ZP0W5Ccgo-aWCCXMz0SBlt-V1LgEtIKT_WO_KCvsAFUWl0uNtosPpi0DNRhY",
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
    
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    responseDSData = loop.run_until_complete(request(urlDS, requestBodyDS, headers))

    # responseDS = requests.post("https://datastore.googleapis.com/v1beta1/projects/cafe-app-200914:export",
    # data=str(bodyDS),
    # headers={
    #     "Authorization":"Bearer ya29.Gl27BZbKv4v_DAhnBpddlJAroKlny_3FmJOF9TMYhYbHSyIbhU5Y1K2-37-Xb4DsA15ZP0W5Ccgo-aWCCXMz0SBlt-V1LgEtIKT_WO_KCvsAFUWl0uNtosPpi0DNRhY",
    #     "Content-Type":"application/json"}
    # )

    print("responseDSData = ")
    print(responseDSData)

    # ### LOAD METADATA FROM CLOUD STORAGE BUCKET TO BIGQUERY ###
    # big_query_service_acct = "cafe-app-54e9e8e2ce3e.json"
    
    # outputUrlPrefix = responseDSData["metadata"]["outputUrlPrefix"]
    # exportedDataPath = str(outputUrlPrefix + "/default_namespace/kind_Wait/default_namespace_kind_Wait.export_metadata")

    # print("exportedDataPath = " + exportedDataPath)

    # urlBQ = "https://www.googleapis.com/bigquery/v2/projects/projectId/jobs:insert"
    # requestBodyBQ = {
    #   "configuration": {
    #     "load": {
    #       "sourceUris": [
    #         exportedDataPath
    #       ],
    #       "sourceFormat": "DATASTORE_BACKUP",
    #       "destinationTable": {
    #         "datasetId": "training",
    #         "projectId": "cafe-app-200914",
    #         "tableId": "batch"
    #       },
    #       "timePartitioning": {
    #         "type": "DAY"
    #       },
    #       "writeDisposition": "WRITE_TRUNCATE" 
    #     }
    #   },
    #   "jobReference": {
    #     "location": "US"
    #   }
    # }
    # bodyBQ = dumps(requestBodyBQ)
    # print("requestBodyBQ = ")
    # print(requestBodyBQ)
    # print("bodyBQ = ")
    # print(bodyBQ)

    # responseBQData = loop.run_until_complete(request(urlBQ, requestBodyBQ, headers))
    # print("responseBQData = ")
    # print(responseBQData)
    # responseBQ = requests.post("https://www.googleapis.com/bigquery/v2/projects/projectId/jobs:insert",
    #     data=str(bodyBQ),
    #     headers={
    #         "Authorization":"Bearer ya29.Gl27BZbKv4v_DAhnBpddlJAroKlny_3FmJOF9TMYhYbHSyIbhU5Y1K2-37-Xb4DsA15ZP0W5Ccgo-aWCCXMz0SBlt-V1LgEtIKT_WO_KCvsAFUWl0uNtosPpi0DNRhY",
    #         "Content-Type":"application/json"}
    #     )
    # print(responseBQ.status_code, responseBQ.reason, responseBQ.text)
    # responseBQData = responseBQ.json()

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
