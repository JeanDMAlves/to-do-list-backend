from database.database import get_database, current_database
from models.user import UserDB, UserCreate, UserPartialUpdate, UserBasic, UserAuthentication
from fastapi import APIRouter, HTTPException, status, Depends, Body, UploadFile, File, Form
from models.models import users
from authenticate.hasher import Hasher

async def get_user_or_404(id: int, database: current_database) -> UserDB:
    select_query = users.select().where(users.c.id == id)
    raw_user = await database.fetch_one(select_query)
    if raw_user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuário não foi encontrado")
    return UserDB(**raw_user)

async def verify_email_exists(email: str, database: current_database) -> bool:
    select_query = users.select().where(users.c.email == email)
    user = await database.fetch_one(select_query)
    if user != None:
        return True
    return False

async def get_user_if_exists(user: UserBasic, database: current_database) -> UserBasic:
    if not (await verify_email_exists(user.email, database)):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuário não foi encontrado")
    return user

async def authenticate_user(user: UserBasic = Depends(get_user_if_exists), database: current_database = current_database):
    hashed_password = await database.fetch_one(f"SELECT password FROM Users WHERE email = '{user.email}'")
    if not (Hasher.verify_password(user.password, *hashed_password)):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Senha incorreta")
    return user