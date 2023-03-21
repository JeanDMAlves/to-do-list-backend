from fastapi import FastAPI, HTTPException
from database.database import get_database, sqlalchemy_engine
from models.models import metadata
from routers.user import router as user_router
from routers.list import router as list_router
from authenticate.authenticate import router as login_router
from authenticate.authenticate import authenticate_user_by_jwt, oauth2_scheme
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(list_router, prefix="/list", tags=["list"])
app.include_router(login_router, prefix="/token", tags=["token"])

@app.on_event("startup")
async def startup():
    await get_database().connect()
    metadata.create_all(sqlalchemy_engine)
    
@app.on_event("shutdown")
async def shutdown():
    await get_database().disconnect()