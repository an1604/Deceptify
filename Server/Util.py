from data.prompt import Prompt



def add_default_prompts(data_storage):
    if not data_storage.get_prompts():
        print("data storage has no prompts")
        data_storage.add_prompt(Prompt(prompt_desc="Hello", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Hi", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Thank you", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Bye", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Sorry", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Why?", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="What did you say?", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="I don't know", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="what are you talking about", is_deletable=False))
