from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arrange.core.database import conn
from arrange.routers import arrange, docs, param, patient, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    yield
    await conn.disconnect()


app = FastAPI(
    lifespan=lifespan,
    docs_url='/swagger',
)

origins = ['http://localhost:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
)

app.include_router(docs.router, tags=['docs'])
app.include_router(users.router, tags=['users'])
app.include_router(arrange.router, tags=['arrange'])
app.include_router(param.router, tags=['param'])
app.include_router(patient.router, tags=['patient'])


@app.get('/')
async def read_root():
    return {'message': 'Working'}
