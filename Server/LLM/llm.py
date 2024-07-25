from langchain_community.llms import Ollama
from scrapegraphai.graphs import SmartScraperGraph

ROLE = """
ROLE: Your role is to get the ID of the person that you talk with.
REMEMBER: keep your answers as short as you can, maximum one line in any case.
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

    def get_answer(self, prompt, event=None):
        answer = self.llm.invoke(ROLE.format(prompt))
        if event:
            event.set()
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

    def scrape(self, url, prompt):
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
    # llm.scrape()
    llm.get_answer("what is 1 + 4")
