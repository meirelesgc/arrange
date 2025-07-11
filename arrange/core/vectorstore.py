from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from arrange.config import Settings

connection_url = Settings()._get_connection_string()

local_vectorstore = PGVector(
    embeddings=OllamaEmbeddings(
        model='qwen2.5-coder:1.5b-base',
        base_url=Settings().OLLAMA_BASE_URL,
    ),
    connection=connection_url,
    use_jsonb=True,
    async_mode=True,
)

vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(
        model='text-embedding-3-small',
        api_key=Settings().OPENAI_API_KEY,
    ),
    connection=connection_url,
    use_jsonb=True,
    async_mode=True,
)


async def get_vectorstore():
    yield vectorstore
