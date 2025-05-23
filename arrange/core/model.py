from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from arrange.config import Settings

model = ChatOpenAI(
    model='gpt-4o-mini',
    api_key=Settings().OPENAI_API_KEY,
)


local_model = ChatOllama(
    model='gemma3:4b',
    base_url=Settings().OLLAMA_BASE_URL,
)


async def get_local_model():
    return local_model


async def get_model():
    return model
