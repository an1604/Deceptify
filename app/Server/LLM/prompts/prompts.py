import os
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate


def get_text_from_file(path):
    with open(path, "r") as f:
        return f.read()


class prompts(object):
    ROLE = SystemMessage(content=get_text_from_file('Server/LLM/prompts/role.txt'))
    PRINCIPLES = get_text_from_file('Server/LLM/prompts/remember.txt')
    KNOWLEDGEBASE_ROLE = SystemMessage(content=get_text_from_file('Server/LLM/prompts/knowledge.txt'))

    def get_role(self, role: str, prompt, history, name='Donald', place='park', target='address',
                 connection='co-worker'):
        principles = self.PRINCIPLES.format(target=target)
        r = role.format(name=name, place=place, target=target, connection=connection, principles=principles)
        return r
