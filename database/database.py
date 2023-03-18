import sqlalchemy
from databases import Database
from fastapi import Depends
from typing import Annotated

DATABASE_URL = "sqlite:///baseTeste.db"
database = Database(DATABASE_URL)
sqlalchemy_engine = sqlalchemy.create_engine(DATABASE_URL)

def get_database() -> Database:
    return database

current_database = Annotated[Database, Depends(get_database)]