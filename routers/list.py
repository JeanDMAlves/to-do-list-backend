from fastapi import APIRouter, HTTPException, status, Depends, Body
from models.list import ListBase, ListDB
from models.models import lists
from databases import Database
from database.database import get_database
from authenticate.authenticate import authenticate_user_by_jwt
router = APIRouter()

@router.get('/AA')
async def algo(x = Depends(authenticate_user_by_jwt)):
    return x 