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
    Column("image", String(length=255), nullable = True),
    Column("register_date", DateTime())
)

lists = Table(
    "Lists",
    metadata,
    Column("id", Integer, primary_key = True, autoincrement = True),
    Column("id_user", Integer, ForeignKey(users.c.id), nullable=False),
    Column("name", String(length=255), nullable = False),
    Column("creation_date", DateTime(), nullable = False)
)

activities = Table(
    "Activities",
    metadata,
    Column("id", Integer, primary_key = True, autoincrement = True),
    Column("id_user", Integer, ForeignKey(users.c.id), nullable=False),
    Column("id_list", Integer, ForeignKey(lists.c.id), nullable=False),
    Column("name", String(length=255), nullable = False),
    Column("description", String(length=255), nullable = True),
    Column("register_date", DateTime(), nullable = False)
)
