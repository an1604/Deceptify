from langchain_community.llms import Ollama
from scrapegraphai.graphs import SmartScraperGraph

ROLE = """
ROLE: Your role is to make sure that you have enough information about the person you talk to.
REMEMBER: keep your answers as short as you can, maximum 2 lines in any case.
Query: {} 
"""

# model_name = 'http://ollama:11434/'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY

# machine = 'ollama'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY

# Scraper configurations
graph_config = {
    "llm": {
        "model": "ollama/llama3",
        "temperature": 0,
        "format": "json",
        "base_url": f"http://{machine}:11434",
    },
    "embeddings": {
        "model": f"http://{machine}:11434/nomic-embed-text",
        "base_url": f"http://{machine}:11434",
    },
    "verbose": True,
}


class Llm(object):
    def __init__(self):
        self.llm = Ollama(model=model_name)
        self.scraper = None

    def get_answer(self, prompt):
        answer = self.llm.invoke(ROLE.format(prompt))
        print(answer)
        return answer

    def run_long_conversation(self):
        prompt = input("You're turn ")
        while not ('exit' in prompt):
            print(f"\n{self.get_answer(prompt)}")
            prompt = input("You're turn ")

    def run_quick_conversation(self):
        prompt = ROLE.format(input("You're turn "))
        while not ('exit' in prompt):
            for chunks in self.llm.stream(prompt):
                print(chunks, end="")
            prompt = ROLE.format(input("You're turn "))

    def scrape(self, url="https://perinim.github.io/projects",
               prompt="List me all the projects with their descriptions"):
        self.scraper = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config
        )
        result = self.scraper.run()
        print(result)
        return result


if __name__ == '__main__':
    llm = Llm()
    #llm.scrape()
    llm.get_answer("what is 1 + 4")
