from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from src.utility.db_utils import get_db
from src.database.models import Todos
from src.routers.auth import get_current_user


# Initialize a new instance of the API Router for admin
router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    
    if not user or user.get("user_role") != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    return db.query(Todos).all()


@router.get("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int=Path(gt=0)):
    
    if not user or user.get("user_role") != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found!")
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    