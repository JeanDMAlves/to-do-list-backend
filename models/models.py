import sqlalchemy
from sqlalchemy import Table, Column, Integer, DateTime, String, ForeignKey

metadata = sqlalchemy.MetaData()

users = Table(
    "Users",
    metadata,
    Column("id", Integer, primary_key = True, autoincrement = True),
    Column("name", String(length=255), nullable = False),
    Column("email", String(length=255), nullable = False),
    Column("password", String(length=255), nullable = False),
    Column("register_date", DateTime())
)

lists = Table(
    "List",
    metadata,
    Column("id", Integer, primary_key = True, autoincrement = True),
    Column("id_user", Integer, ForeignKey(users.c.id), nullable=False),
    Column("name", String(length=255), nullable = False),
    Column("creation_date", DateTime())
)