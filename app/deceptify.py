from app import create_app
from app.Server.LLM.llm import Llm

llm = Llm()
app = create_app()
