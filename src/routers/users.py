from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from src.utils.db_utils import get_db
from src.database.models import Users
from src.routers.auth import get_current_user
from src.models.todos import UserVerification



router = APIRouter(
    prefix='/user',
    tags=['user']
)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Password!")
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    
    db.add(user_model)
    db.commit()
    