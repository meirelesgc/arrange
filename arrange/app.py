from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from arrange.core.database import conn
from arrange.routers import arrange, docs, param, patient, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    app.state.last_request_time = None
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


@app.middleware('http')
async def track_last_request_time(request: Request, call_next):
    request.app.state.last_request_time = datetime.now(UTC)
    response = await call_next(request)
    return response


app.include_router(docs.router, tags=['docs'])
app.include_router(users.router, tags=['users'])
app.include_router(arrange.router, tags=['arrange'])
app.include_router(param.router, tags=['param'])
app.include_router(patient.router, tags=['patient'])


@app.get('/')
async def read_root():
    return {'message': 'Working'}


@app.get('/last-request')
async def get_last_request_time(request: Request):
    last_time = request.app.state.last_request_time
    if last_time is None:
        return {'last_request_time': None}
    return {'last_request_time': last_time.isoformat()}
