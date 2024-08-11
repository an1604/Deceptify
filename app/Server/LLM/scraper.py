from scrapegraphai.graphs import SmartScraperGraph

# model_name = 'http://ollama:11434/'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
# model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
model_name = 'tinyllama'

# machine = 'ollama'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY



class Scraper(object):
    def __init__(self):
        # Scraper configurations
        self.graph_config = {
            "llm": {
                "model": "ollama/llama3",
                "temperature": 0,
                "format": "json",
                "base_url": f"http://{machine}:11434",
            },
            "embeddings": {
                "model": "ollama/nomic-embed-text",
                "base_url": f"http://{machine}:11434",
            },
            "verbose": True,
        }
        self.scraper = None

    def scrape(self, url, prompt):
        self.scraper = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=self.graph_config
        )
        result = self.scraper.run()
        print(result)
        return result
