import os 
from pydantic import BaseModel
from typing import Optional, Annotated
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
from datetime import datetime, timedelta
from routers.user import authenticate_user, get_user_if_exists
from models.user import UserBasic
from models.models import users
from databases import Database
from database.database import database, get_database
from models.user import UserAuthentication

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class Token(BaseModel):
    access_token: str
    token_type: str
    
router = APIRouter()

async def get_authenticated_user_info(user_email: str) -> UserAuthentication:
    database = get_database()
    select_query = users.select().where(users.c.email == user_email)
    user = await database.fetch_one(select_query)
    if user:
        return UserAuthentication(id = user.id, email = user.email)
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Usuário não foi encontrado")
    
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user_by_jwt(token: str = Depends(oauth2_scheme)) -> UserAuthentication:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    user = await get_authenticated_user_info(user_email)
    return user
    
@router.post('/', response_model=Token)
async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), database: Database = Depends(get_database)):
    user = UserBasic(email=form_data.username, password=form_data.password)
    user = await get_user_if_exists(user, database)
    user = await authenticate_user(user, database)
    acess_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    acess_token = create_access_token(data = {"sub": user.email}, expires_delta=acess_token_expires)
    return {"access_token": acess_token, "token_type": "bearer"}

currentUser = Annotated[UserAuthentication, Depends(authenticate_user_by_jwt)]

# @router.get('/TESTE')
# async def teste(user: currentUser):
#     return user.dict()