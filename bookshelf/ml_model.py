import googleapiclient.discovery
import logging, requests, os
from subprocess import call

def retrain():
    # TODO: Export entities into a csv for the training batch
    # TODO: Delete entities from the datastore
    # TODO: Concatenate csv with existing training data
    # TODO: Retrain

    GOOGLE_APPLICATION_CREDENTIALS='cafe-app-f9f9134f1cd3.json'

    # r = requests.post("https://datastore.googleapis.com/v1/projects/cafe-app-200914:export", data={"outputUrlPrefix": "gs://cafe-app-datastore"}, headers={"Authorization": "Bearer ya29.Gl26BXojlqcmKWRshyA8hcIMvJFHrBBzZsioda3joAk5MGQvUVNBaSfdpWbF-O3RkA5I6uchonazVyfXeNS6-R4kw3rcdJCcmw7S9596rfKqbn6bFP2q8OCOCg8LdNQ", "Content-Type": "application/json"})
    # print(r.status_code, r.reason, r.text)

    # call(["gcloud", ""])
    os.system("gcloud datastore export gs://cafe-app-datastore")
    logging.info("RETRAIN UNIMPLEMENTED")
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
