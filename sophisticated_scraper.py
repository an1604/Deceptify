from scrapegraphai.graphs import SmartScraperGraph
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API')

graph_config = {
    "llm": {
        "api_key": OPENAI_API_KEY,
        "model": "gpt-3.5-turbo",
    },
}

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the paper's articles",
    # also accepts a string with the already downloaded HTML code
    source="https://huggingface.co/papers",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
