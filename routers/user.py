from fastapi import APIRouter, HTTPException, status, Depends, Body, UploadFile, File, Form
from models.user import UserDB, UserCreate, UserPartialUpdate, UserBasic
from models.models import users
from databases import Database
from database.database import get_database, current_database
from authenticate.hasher import Hasher
import shutil
from typing import Optional
from pydantic import Field, EmailStr
import os

router = APIRouter()

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
     
@router.delete("/", status_code = status.HTTP_200_OK)
async def delete_user(database: current_database, user: UserBasic = Depends(authenticate_user)) -> str:
    delete_query = users.delete().where(users.c.email == user.email)
    await database.execute(query=delete_query)
    file_path = f"./assets/{user.email}.jpg"
    if os.path.isfile(file_path):
        os.remove(file_path)
    return "Usuário deletado com sucesso"

@router.put("/password", response_model = str, status_code = status.HTTP_200_OK)
async def update_password(database: current_database, user: UserBasic = Depends(authenticate_user), new_password: str = Body(...)):
    new_password_hashed = Hasher.get_password_hash(new_password)
    update_query = users.update().where(users.c.email == user.email).values(password=new_password_hashed)
    await database.execute(query=update_query)
    return "Senha atualizada com sucesso"
    
@router.post("/", response_model = str, status_code = status.HTTP_201_CREATED)
async def create_user(
    database: current_database, 
    file: UploadFile = File(...), 
    email: EmailStr = Body(...),
    name: str = Body(...),
    password: str = Body(...)
    ) -> str:
    if await verify_email_exists(email, database):
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Usuário já está cadastrado") 
    os.makedirs('./assets/', exist_ok=True)
    
    path_image = f"./assets/{email}.jpg"
    
    user = UserCreate(
        name = name,
        email = email,
        password = Hasher.get_password_hash(password),
        image = path_image
    )
    
    with open(f"{path_image}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    insert_query = users.insert().values(user.dict())
    user_id = await database.execute(insert_query)
     
    user_db = await get_user_or_404(user_id, database)
    
    return "Usuário criado com sucesso"

@router.post("/AAA")
async def abcd(image: UploadFile = File(...)):
    return {"file_name": image.filename, "content_type": image.content_type}


@router.get("/list", response_model = dict, status_code = status.HTTP_200_OK)
async def list_users(database: current_database) -> dict:
    users_email = await database.fetch_all("SELECT name, email FROM Users")
    return {"users": users_email}