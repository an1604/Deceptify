from data.prompt import Prompt


def add_default_prompts(data_storage):
    print("adding prompts")
    if not data_storage.get_prompts():
        print("data storage has no prompts")
        data_storage.add_prompt(Prompt(prompt_desc="Hello"))
        data_storage.add_prompt(Prompt(prompt_desc="Hi"))
        data_storage.add_prompt(Prompt(prompt_desc="Thank you"))
        data_storage.add_prompt(Prompt(prompt_desc="Bye"))
        data_storage.add_prompt(Prompt(prompt_desc="Sorry"))
        data_storage.add_prompt(Prompt(prompt_desc="Why?"))
        data_storage.add_prompt(Prompt(prompt_desc="What did you say?"))
        data_storage.add_prompt(Prompt(prompt_desc="I don't know"))
        data_storage.add_prompt(Prompt(prompt_desc="what are you talking about"))
