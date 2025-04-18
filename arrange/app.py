from contextlib import asynccontextmanager

from fastapi import FastAPI

from arrange.core.database import conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    yield
    await conn.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def read_root():
    return {'message': 'Working'}
