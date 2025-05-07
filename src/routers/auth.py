import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from jose import jwt, JWTError
from src.models.todos import CreateUserRequest, Token
from src.database.models import Users
from src.utils.db_utils import get_db


# load from .env
load_dotenv()



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


async def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.user == username).first()
    
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user


async def create_access_token(username: str, user_id: int, role: str, expire_delta: timedelta):
    encode = {
        'sub': username,
        'id': user_id,
        'role': role
    }
    
    expires = datetime.now(timezone.utc) + expire_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM) 


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        
        if not username or not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user!")
        
        return {"username": username, "id": user_id, "user_role": user_role}
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user!")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[Session, Depends(get_db)], create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        user=create_user_request.user,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )
    
    db.add(create_user_model)
    db.commit()
    

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user!")
    
    token = await create_access_token(user.user, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}