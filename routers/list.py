from fastapi import APIRouter, HTTPException, status, Depends, Body
from models.list import ListBase, ListDB
from models.models import lists
from databases import Database
from database.database import get_database, current_database
from authenticate.authenticate import authenticate_user_by_jwt, currentUser
from typing import List
from routers.activity import router as activity_router

router = APIRouter()
router.include_router(activity_router, prefix="/task", tags=["list"])


async def check_list_exists(name: str, user_id: int, database):
    select_query =  f"""SELECT * FROM Lists WHERE id_user = {user_id} and name = '{name}'"""
    exists = await database.fetch_one(select_query)
    if exists != None:
        return True
    return False

@router.get('/', status_code = status.HTTP_200_OK)
async def get_all_lists(user: currentUser, database: current_database):
    select_query = f"""SELECT id, name, creation_date FROM Lists WHERE id_user = {user.id}"""
    listas = await database.fetch_all(query=select_query)
    return listas

@router.post('/', status_code = status.HTTP_201_CREATED)
async def post_new_list(name: str, user: currentUser, database: current_database):
    if await check_list_exists(name, user.id, database):
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Lista já existe!")
    new_list = ListBase(name = name, id_user = user.id)
    insert_query = lists.insert().values(new_list.dict())
    list_id = await database.execute(insert_query)
    return "Lista cadastrada com sucesso!"

@router.delete('/', status_code = status.HTTP_200_OK)
async def delete_list_from_user(name: str, user: currentUser, database: current_database):
    if not (await check_list_exists(name, user.id, database)):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Lista não foi encontrada!")
    delete_query = lists.delete().where((lists.c.name == name) and (lists.c.id_user == user.id))
    await database.execute(query = delete_query)
    return "Lista deletada com sucesso"