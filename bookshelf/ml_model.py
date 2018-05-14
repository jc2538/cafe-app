import googleapiclient.discovery
import logging, requests
from json import dumps
from subprocess import call
from google_auth_oauthlib.flow import InstalledAppFlow

def get_token():
    # CLIENT_ID = 795479451499-r06p1nlp3dgpiuhtba3pvblootc6afmv.apps.googleusercontent.com
    # CLIENT_SECRET = Z2H7LsVOQN1gohstucRi9mRY
    flow = InstalledAppFlow.from_client_secrets_file(
        '/Users/jessicachen/Documents/College/CS5412/cafe-app/bookshelf/client_secret_795479451499-83ugvgq1giti1lusmufu1cnotf22v4mv.apps.googleusercontent.com.json',
        scopes=['https://www.googleapis.com/auth/drive.metadata'])
    credentials = flow.run_console()
    print("credentials")
    print(credentials)
    print("end credentials")
    return credentials 

def retrain():
    # TODO: Export entities into a csv for the training batch
    # TODO: Delete entities from the datastore
    # TODO: Concatenate csv with existing training data
    # TODO: Retrain

    GOOGLE_APPLICATION_CREDENTIALS='cafe-app-f9f9134f1cd3.json'

    requestBody = {
        "entityFilter": {
            "kinds": ["Wait"],
            "namespaceIds": [""]
            },
        "outputUrlPrefix": "gs://cafe-app-datastore"
        }
    body = dumps(requestBody)
    credentials_output = get_token()
    r = requests.post("https://datastore.googleapis.com/v1beta1/projects/cafe-app-200914:export",
        data=str(body),
        headers={
            "Authorization":credentials_output,
            "Content-Type":"application/json"}
        )
    
    print(r.status_code, r.reason, r.text)

    responseData = r.json()
    outputUrlPrefix = responseData["metadata"]["outputUrlPrefix"]
    exportedDataPath = outputUrlPrefix + "/default_namespace/kind_Wait/default_namespace_kind_Wait.export_metadata"
    print(exportedDataPath)

    print("RETRAIN UNIMPLEMENTED")

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
