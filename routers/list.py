from fastapi import APIRouter, HTTPException, status, Depends, Body
from models.list import ListBase, ListDB
from models.models import lists
from databases import Database
from database.database import get_database
from authenticate.authenticate import authenticate_user_by_jwt
from typing import List

router = APIRouter()

async def check_list_exists(name: str, user_id: int, database):
    select_query = lists.select().where((lists.c.id_user == user_id) and (lists.c.name == name))
    exists = await database.fetch_one(select_query)
    if exists != None:
        return True
    return False

@router.get('/all', status_code = status.HTTP_200_OK)
async def get_all_lists(user = Depends(authenticate_user_by_jwt), database: Database = Depends(get_database)):
    select_query = f"""SELECT id, name, creation_date FROM Lists WHERE id_user = {user.id}"""
    listas = await database.fetch_all(query=select_query)
    return listas

@router.post('/register', status_code = status.HTTP_201_CREATED)
async def post_new_list(name: str, user = Depends(authenticate_user_by_jwt), database: Database = Depends(get_database)):
    if await check_list_exists(name, user.id, database):
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Lista já existe!")
    new_list = ListBase(name = name, id_user = user.id)
    insert_query = lists.insert().values(new_list.dict())
    list_id = await database.execute(insert_query)
    return "Lista cadastrada com sucesso!"

@router.delete('/delete', status_code = status.HTTP_200_OK)
async def delete_list_from_user(name: str, user = Depends(authenticate_user_by_jwt), database: Database = Depends(get_database)):
    if not (await check_list_exists(name, user.id, database)):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Lista não foi encontrada!")
    delete_query = lists.delete().where((lists.c.name == name) and (lists.c.id_user == user.id))
    await database.execute(query = delete_query)
    return "Lista deletada com sucesso"