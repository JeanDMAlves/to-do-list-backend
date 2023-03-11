from fastapi import APIRouter, HTTPException, status, Depends, Body
from models.user import UserDB, UserCreate, UserPartialUpdate, UserBasic
from models.models import users
from databases import Database
from database.database import get_database
from authenticate.hasher import Hasher

router = APIRouter()

async def get_user_or_404(id: int, database: Database = Depends(get_database)) -> UserDB:
    select_query = users.select().where(users.c.id == id)
    raw_user = await database.fetch_one(select_query)
    if raw_user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuário não foi encontrado")
    return UserDB(**raw_user)

async def verify_email_exists(email: str, database: Database = Depends(get_database)) -> bool:
    select_query = users.select().where(users.c.email == email)
    user = await database.fetch_one(select_query)
    if user != None:
        return True
    return False

async def get_user_if_exists(user: UserBasic, database: Database = Depends(get_database)) -> UserBasic:
    if not (await verify_email_exists(user.email, database)):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuário não foi encontrado")
    return user

async def authenticate_user(user: UserBasic = Depends(get_user_if_exists), database: Database = Depends(get_database)):
    hashed_password = await database.fetch_one(f"SELECT password FROM Users WHERE email = '{user.email}'")
    if not (Hasher.verify_password(user.password, *hashed_password)):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Senha incorreta")
    return user
     
@router.delete("/delete", status_code = status.HTTP_200_OK)
async def delete_user(user: UserBasic = Depends(authenticate_user), database: Database = Depends(get_database)) -> str:
    delete_query = users.delete().where(users.c.email == user.email)
    await database.execute(query=delete_query)
    return "Usuário deletado com sucesso"

@router.put("/password", response_model = str, status_code = status.HTTP_200_OK)
async def update_password(user: UserBasic = Depends(authenticate_user), new_password: str = Body(...), database: Database = Depends(get_database)):
    new_password_hashed = Hasher.get_password_hash(new_password)
    update_query = users.update().where(users.c.email == user.email).values(password=new_password_hashed)
    await database.execute(query=update_query)
    return "Senha atualizada com sucesso"
    
@router.post("/register", response_model = str, status_code = status.HTTP_201_CREATED)
async def create_user(user: UserCreate = Body(...), database: Database = Depends(get_database)) -> str:
    if await verify_email_exists(user.email, database):
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Usuário já está cadastrado") 
    user.password = Hasher.get_password_hash(user.password)
    insert_query = users.insert().values(user.dict())
    user_id = await database.execute(insert_query)
    user_db = await get_user_or_404(user_id, database)
    return "Usuário criado com sucesso"

@router.get("/list", response_model = dict, status_code = status.HTTP_200_OK)
async def list_users(database: Database = Depends(get_database)) -> dict:
    users_email = await database.fetch_all("SELECT name, email FROM Users")
    return {"users": users_email}