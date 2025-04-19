from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from arrange.core.connection import Connection
from arrange.models import user_models
from arrange.repositories import user_repository
from arrange.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


async def post_user(conn: Connection, user: user_models.CreateUser):
    user = user_models.User(**user.model_dump(), role='DEFAULT')
    user.password = get_password_hash(user.password)
    await user_repository.post_user(conn, user)
    return user


async def get_user(conn: Connection, id: UUID = None, email: EmailStr = None):
    users = await user_repository.get_user(conn, id, email)
    return users


async def put_user(conn: Connection, user: user_models.User):
    user.updated_at = datetime.now()
    user.password = get_password_hash(user.password)
    await user_repository.put_user(conn, user)
    return user


async def delete_user(conn: Connection, id: UUID = None):
    users = await user_repository.delete_user(conn, id)
    return users


async def login_for_access_token(
    conn: Connection,
    form_data: OAuth2PasswordRequestForm,
):
    user = await get_user(conn, None, form_data.username)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    if not verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    access_token = create_access_token(data={'sub': user['email']})
    return {'access_token': access_token, 'token_type': 'bearer'}
