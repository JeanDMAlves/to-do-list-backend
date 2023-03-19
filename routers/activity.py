from fastapi import APIRouter, HTTPException, status, Depends, Body
from database.database import get_database, current_database
from authenticate.authenticate import authenticate_user_by_jwt, currentUser
from models.activity import ActivityBase, ActivityDB
from models.models import lists, activities
from typing import Optional, List

router = APIRouter()

async def get_list_id_or_404(name: str, user_id: int, database):
    select_query = f"""SELECT * FROM Lists WHERE id_user = {user_id} and name = '{name}'"""
    exists = await database.fetch_one(select_query)
    if exists == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Lista não existe")
    return exists.id

async def task_already_exists(name: str, id_list: int, id_user: int, database):
    select_query = f"""SELECT * 
                       FROM Activities 
                       WHERE 
                       id_user={id_user} and id_list={id_list} and name='{name}'"""
    task = await database.fetch_one(select_query)
    if task != None:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Tarefa já existe nessa lista")

async def get_task_id(name: str, id_list: int, id_user: int, database):
    select_query = f"""SELECT * 
                       FROM Activities 
                       WHERE 
                       id_user={id_user} and id_list={id_list} and name='{name}'"""
    task: ActivityDB = await database.fetch_one(select_query)
    if task != None:
        return task.id
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Tarefa não foi encontrada")

@router.get('/all', status_code = status.HTTP_200_OK, response_model= List[ActivityDB])
async def get_all_tasks(user: currentUser, database: current_database):
    select_query = f"""SELECT * FROM Activities WHERE id_user = {user.id}"""
    tasks = await database.fetch_all(query=select_query)
    return tasks

@router.post('/', status_code = status.HTTP_201_CREATED, response_model = str)
async def post_task_in_list(
    user: currentUser, 
    database: current_database, 
    name: str = Body(...), 
    description: Optional[str] = Body(None),
    name_list: str = Body(...)
):
    list_id = await get_list_id_or_404(name=name_list, user_id = user.id, database = database)
    await task_already_exists(name, id_list=list_id, id_user=user.id, database=database)
    task = ActivityBase(name=name, id_user=user.id, description=description, id_list=list_id)
    insert_query = activities.insert().values(task.dict())
    await database.execute(insert_query)
    return 'Tarefa adicionada na lista desejada com sucesso'

@router.delete('/', status_code=status.HTTP_200_OK)
async def delete_task_from_list(
    user: currentUser, 
    database: current_database,
    name: str = Body(...), 
    name_list: str = Body(...)
):
    list_id = await get_list_id_or_404(name=name_list, user_id = user.id, database = database)
    task_id = await get_task_id(name, id_list=list_id, id_user=user.id, database=database)
    delete_query = activities.delete().where((activities.c.id == task_id) and (activities.c.id_user == user.id) and (activities.c.id_list == list_id))
    await database.execute(query=delete_query)
    return "Tarefa deletada com sucesso"

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[ActivityDB])
async def get_tasks_from_list(user: currentUser, database: current_database, name_list: str):
    list_id = await get_list_id_or_404(name=name_list, user_id = user.id, database = database)
    select_query = f"""SELECT * FROM Activities WHERE id_user = {user.id} and id_list = {list_id}"""
    tasks = await database.fetch_all(query=select_query)
    return tasks