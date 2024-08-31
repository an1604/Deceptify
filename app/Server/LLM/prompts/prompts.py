import os
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_text_from_file(path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_to_file = os.path.join(script_dir, path)
    logging.info(f"Reading text from file: {path_to_file}")
    with open(path_to_file, "r") as f:
        return f.read()


class Prompts(object):
    ROLE = None

    @staticmethod
    def set_role(attack_purpose):
        logging.info(f"Setting role for attack purpose: {attack_purpose}")
        Prompts.ROLE = PromptTemplate.from_template(
            get_text_from_file(f'{attack_purpose.lower()}/{attack_purpose}Role.txt'))

    @staticmethod
    def get_principles(target='address'):
        logging.info(f"Getting principles for target: {target}")
        return Prompts.PRINCIPLES.format(target=target)

    @staticmethod
    def get_role(role: str, name='Donald', place='park', target='address',
                 connection='co-worker'):
        logging.info(
            f"Getting role with parameters: role={role}, name={name}, place={place}, target={target}, connection={connection}")
        principles = Prompts.get_principles()
        r = role.format(name=name, place=place, target=target, connection=connection, principles=principles)
        return r
