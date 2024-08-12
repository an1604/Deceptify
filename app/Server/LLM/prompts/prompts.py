import os
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate


def get_text_from_file(path):
    with open(path, "r") as f:
        return f.read()


class Prompts(object):
    ROLE = None

    # PRINCIPLES = get_text_from_file('Server/LLM/prompts/remember.txt')
    # KNOWLEDGEBASE_ROLE = SystemMessage(content=get_text_from_file('knowledge.txt'))

    @staticmethod
    def set_role(attack_purpose):
        Prompts.ROLE = PromptTemplate.from_template(
            get_text_from_file(f'{attack_purpose}Role.txt'))

    @staticmethod
    def get_principles(target='address'):
        return prompts.PRINCIPLES.format(target=target)

    @staticmethod
    def get_role(role: str, name='Donald', place='park', target='address',
                 connection='co-worker'):
        principles = prompts.get_principles()
        r = role.format(name=name, place=place, target=target, connection=connection, principles=principles)
        return r
