from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE: str
    PG_USER: str
    PASSWORD: str
    HOST: str
    PORT: int

    OPENAI_API_KEY: str

    OLLAMA_BASE_URL: str = 'http://localhost:11434'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    def get_connection_string(self) -> str:
        return f'postgresql://{self.PG_USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}'

    def _get_connection_string(self) -> str:
        return f'postgresql+psycopg://{self.PG_USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}'
