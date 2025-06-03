from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector

from arrange.config import Settings

connection_url = Settings()._get_connection_string()

vectorstore = PGVector(
    embeddings=OllamaEmbeddings(
        model='qwen2.5-coder:1.5b-base', base_url=Settings().OLLAMA_BASE_URL
    ),
    connection=connection_url,
    use_jsonb=True,
    async_mode=True,
)


async def get_vectorstore():
    yield vectorstore
