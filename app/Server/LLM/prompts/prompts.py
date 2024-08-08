import os
from langchain_core.prompts import PromptTemplate


def get_text_from_file(path):
    with open(path, "r") as f:
        return f.read()


def replace_target_info(content, param, param_name):
    text = content.replace(param_name, param)
    return text


def get_role(role: str, prompt, history, place='park', target='address', connection='co-worker'):
    r = role.format(place=place, target=target, connection=connection,prompt=prompt,history= history)
    return r


ROLE = get_text_from_file('Server/LLM/prompts/role.txt')

KNOWLEDGEBASE_ROLE = get_text_from_file('Server/LLM/prompts/knowledge.txt')

ROLE_TEMPLATE = 'Role: {}\n{}'
CONTEX_TEMPLATE = '\nContex: {}\n'
PROMPT_TEMPLATE = '{}\n{}{}{}'
