from contextlib import asynccontextmanager

from fastapi import FastAPI

from arrange.core.database import conn
from arrange.routers import arrange, docs, param, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    yield
    await conn.disconnect()


app = FastAPI(
    lifespan=lifespan,
    docs_url='/swagger',
)

app.include_router(docs.router, tags=['docs'])
app.include_router(users.router, tags=['users'])
app.include_router(arrange.router, tags=['arrange'])
app.include_router(param.router, tags=['param'])


@app.get('/')
async def read_root():
    return {'message': 'Working'}
