from fastapi import APIRouter, HTTPException, status, Depends, Body, UploadFile, File, Form
from fastapi.responses import FileResponse
from models.user import UserDB, UserCreate, UserPartialUpdate, UserBasic, UserAuthentication
from models.models import users
from databases import Database
from database.database import get_database, current_database
from authenticate.hasher import Hasher
from authenticate.user import *
from authenticate.authenticate import authenticate_user_by_jwt, currentUser
import shutil
from typing import Optional
from pydantic import Field, EmailStr
import os

router = APIRouter()

base_path_images = "./assets"
     
@router.delete("/", status_code = status.HTTP_200_OK)
async def delete_user(database: current_database, user: UserBasic = Depends(authenticate_user)) -> str:
    delete_query = users.delete().where(users.c.email == user.email)
    await database.execute(query=delete_query)
    file_path = f"{base_path_images}/{user.email}.jpg"
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
    os.makedirs(f'{base_path_images}/', exist_ok=True)
    
    path_image = f"{base_path_images}/{email}.jpg"
    
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

@router.get("/list", response_model = dict, status_code = status.HTTP_200_OK)
async def list_users(database: current_database) -> dict:
    users_email = await database.fetch_all("SELECT name, email FROM Users")
    return {"users": users_email}

@router.get("/image", status_code = status.HTTP_200_OK)
async def return_image_of_user(user = Depends(authenticate_user_by_jwt)):
    path = f"{base_path_images}/{user.email}.jpg"
    return FileResponse(path)

@router.put("/image", status_code = status.HTTP_200_OK, response_model = str)
async def change_user_image(user = Depends(authenticate_user_by_jwt), file: UploadFile = File(...)):
    path_image = f"{base_path_images}/{user.email}.jpg"
    with open(f"{path_image}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return "Foto alterada com sucesso"
