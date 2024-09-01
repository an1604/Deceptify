import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

URL = os.getenv('SERVER_URL')


def new_attack_request(mimic_name, attack_purpose):
    try:
        logging.info("Sending new_attack_request to the server.")
        response = requests.post(f'{URL}/new_attack', json={
            'mimic_name': mimic_name,
            'attack_purpose': attack_purpose
        })
        logging.info(f"Response received with status code: {response.status_code}")

        if response.status_code == 200:
            try:
                task_id = response.json().get('req_id')
                logging.info(f"New attack task created successfully with task_id: {task_id}")
                return task_id
            except requests.exceptions.JSONDecodeError:
                logging.error("Failed to decode JSON response. Raw response content:")
                logging.error(response.text)
                return None
        else:
            logging.warning(f"Unexpected status code received: {response.status_code}. Response: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error while making new_attack_request: {e}")
        return None


def generate_answer_request(task_id, prompt,chat_history):
    try:
        logging.info("Sending generate_answer_request to the server.")
        response = requests.post(f'{URL}/generate_answer', json={
            'task_id': task_id,
            'prompt': prompt
        })
        logging.info(f"Response received with status code: {response.status_code}")

        if response.status_code == 200:
            try:
                success = response.json().get('status')
                if success == "success":
                    logging.info(f"Answer generation initiated successfully for task_id: {task_id}")
                    return task_id
                logging.warning("Server response indicates failure: " + response.text)
                return None
            except requests.exceptions.JSONDecodeError:
                logging.error("Failed to decode JSON response. Raw response content:")
                logging.error(response.text)
                return None
        else:
            logging.warning(f"Unexpected status code received: {response.status_code}. Response: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error while making generate_answer_request: {e}")
        return None


def get_llm_answer_request(task_id):
    try:
        get_llm_result_url = f'{URL}/get_llm_result/{task_id}'
        logging.info(f"Sending get_llm_answer_request for task_id: {task_id}")
        response = requests.get(get_llm_result_url)
        logging.info(f"Response received with status code: {response.status_code}")

        if response.status_code == 200:
            answer = response.json().get('answer')
            if answer:
                logging.info(f"Answer received for task_id {task_id}: {answer}")
                return answer
            logging.warning(f"No answer found in response for task_id: {task_id}. Response: {response.text}")
            return None
        elif response.status_code == 202:
            logging.info(f"Task {task_id} is still pending.")
            return None
        else:
            logging.warning(f"Unexpected status code received: {response.status_code}. Response: {response.text}")
            return None
    except requests.exceptions.JSONDecodeError:
        logging.error("Failed to decode JSON response. Raw response content:")
        logging.error(response.text)
        return None
    except Exception as e:
        logging.error(f"Error while making get_llm_answer_request: {e}")
        return None
