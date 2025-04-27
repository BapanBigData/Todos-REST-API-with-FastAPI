from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from src.models.todos import CreateUserRequest
from src.database.models import Users
from src.utility.db_utils import get_db



router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.user == username).first()
    
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return True


@router.post("/auth", status_code=status.HTTP_201_CREATED)
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
    

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        return 'failed'
    
    return 'success'