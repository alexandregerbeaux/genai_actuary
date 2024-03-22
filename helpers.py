import streamlit as st
import requests
import json
import pandas as pd
import os
import datarobotx as drx


CONVERSATION_HISTORY = "data/conversation_history.csv"

class DataRobotPredictionError(Exception):
    """Raised if there are issues getting predictions from DataRobot"""


def topic_guard(prompt):
#    {'flagged': False,
# 'raw_outputs': {'sequence': 'are you able to sell an insurance policy?',
#  'labels': ['insurance topic', 'non insurance topic'],
#  'scores': [0.9870773553848267, 0.01292266882956028]}}

    drx.Context(token=st.secrets["API_KEY"], endpoint="https://app.datarobot.com/api/v2")

    guard_deployment = drx.Deployment.from_url(
        url='https://app.datarobot.com/deployments/6524a1ea013eb2c0df303730/overview'
    )

    response = guard_deployment.predict_unstructured(
        {
            'sequences': prompt,
            'candidate_labels': ['insurance topic', 'non insurance topic'],
            'permitted_labels': ['insurance topic']
        }
    )

    return response


def init_config ():

    if "guard_model_deployment_id" not in st.session_state:
        st.session_state.guard_model_deployment_id = st.secrets["DEFAULT_GUARD_MODEL_DEPLOYMENT_ID"]

    if "genai_model_deployment_id" not in st.session_state:
        st.session_state.genai_model_deployment_id = st.secrets["DEFAULT_GENAI_MODEL_DEPLOYMENT_ID"]



def make_datarobot_deployment_predictions(data, content_type, deployment_id):

    api_key = st.secrets["API_KEY"]
    datarobot_key = st.secrets["DATAROBOT_KEY"]
    api_url = st.secrets["API_URL"]

    # Set HTTP headers. The charset should match the contents of the file.
    headers = {
        'Content-Type': content_type,
        'Authorization': 'Bearer {}'.format(api_key),
        'DataRobot-Key': datarobot_key,
    }

    url = api_url.format(deployment_id=deployment_id)

    # Make API request for predictions
    predictions_response = requests.post(
        url,
        data=data,
        headers=headers,
    )
    _raise_dataroboterror_for_status(predictions_response)
    return predictions_response.json()





def _raise_dataroboterror_for_status(response):
    """Raise DataRobotPredictionError if the request fails along with the response returned"""
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        err_msg = '{code} Error: {msg}'.format(
            code=response.status_code, msg=response.text)
        raise DataRobotPredictionError(err_msg)

def deduplicate_preserve_order(seq):
    seen = set()
    deduplicated = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            deduplicated.append(item)
    return deduplicated

def ask_generative_model(generative_model_deployment_id, prompt):
    body = [{"promptText": prompt}]
    response = make_datarobot_deployment_predictions(json.dumps(body), "application/json", generative_model_deployment_id)
    r = response["data"][0]["prediction"]

    l = r[r.find('Citations') + 11:]
    l2 = l[:l.find('}]')+2]
    l3 = eval(l2)
    my_list = [f"document {i['source']} at page {i['page']}" for i in l3]
    l4 = deduplicate_preserve_order(my_list)
    #unique_list = list(set(my_list))
    #unique_list = [x for x in my_list if x not in unique_list]
    #l4=unique_list
    if len(l4)==0:
        citations = ''
    elif len(l4)==1:
        citations = '\nfor further reference please refer to:' + l4
    else:
        citations = '**Reference:**'+ ' \n\n- '+l4[0] + ' \n\n- ' +' \n\n- '.join(l4[1:]) + ''

    confidence_score = float(r[r.find('Rouge1: ') + len('Rouge1: '):])


    return r[:r.find('Citations')]+citations, confidence_score

def ask_guard_model(guard_model_deployment_id, prompt):
    response = make_datarobot_deployment_predictions(json.dumps([{"text": prompt}]), "application/json", guard_model_deployment_id)
    ret_toxic =  response["data"][0]
    toxic_prediction_label = ret_toxic["prediction"]
    toxic_value = ret_toxic["predictionValues"][0]["value"]
    return toxic_prediction_label,toxic_value

def get_custom_metric_id(deployment_id):
    """List custom metrics defined in a deployment"""
    route = "{}/deployments/{}/customMetrics/"

    datarobot_key = st.secrets["DATAROBOT_KEY"]
    api_key = st.secrets["API_KEY"]

    headers = {
        'Authorization': 'Bearer {}'.format(api_key),
        'DataRobot-Key': datarobot_key,
    }

    response = requests.get(
        url=route.format(st.secrets["DR_ENDPOINT"], deployment_id), headers=headers
    )

    return response.json()["data"][0]["id"]

def submit_metric(deployment_id, timestamp, cm_id) -> None:

    route = "{}/deployments/{}/customMetrics/{}/fromJSON/"
    model_package_id = "658caa794e85fdf160b120ba"

    datarobot_key = st.secrets["DATAROBOT_KEY"]
    api_key = st.secrets["API_KEY"]

    headers = {
        'Authorization': 'Bearer {}'.format(api_key),
        'DataRobot-Key': datarobot_key,
    }

    rows = [{"timestamp": timestamp.isoformat(), "value": 1}]
    json = {
        "buckets": rows,
        "modelPackageId": model_package_id,
    }

    response = requests.post(
        url=route.format(st.secrets["DR_ENDPOINT"], deployment_id, cm_id), json=json, headers=headers
    )

    response.raise_for_status()

def write_history(datetime, question, answer, is_violation):
    is_history()
    df = pd.read_csv(CONVERSATION_HISTORY)
    df = pd.concat(
        (
            df,
            (
                pd.DataFrame(
                    {
                        "datetime": [datetime],
                        "question": [question],
                        "answer": [answer],
                        "is_violation": [is_violation],
                    }
                )
            ),
        )
    )
    df.to_csv(CONVERSATION_HISTORY, index=False)

def is_history():
    if not os.path.exists(CONVERSATION_HISTORY):
        with open(CONVERSATION_HISTORY, "x") as f:
            f.write("datetime,question,answer,is_violation")

def clean_history():
    if os.path.exists(CONVERSATION_HISTORY):
        os.remove(CONVERSATION_HISTORY)
