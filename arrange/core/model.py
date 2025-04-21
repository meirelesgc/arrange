from langchain_ollama import ChatOllama

model = ChatOllama(model='gemma3:4b')


async def get_local_model():
    return model
