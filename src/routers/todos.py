from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from src.utility.db_utils import get_db
from src.database.models import Todos
from src.models.todos import TodoRequest
from src.routers.auth import get_current_user


# Initialize a new instance of the API Router for Todos
router = APIRouter(
    tags=["todos"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: Annotated[Session, Depends(get_db)]):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    return db.query(Todos).filter(Todos.user_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: Annotated[Session, Depends(get_db)], todo_id: int=Path(gt=0)):
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.user_id == user.get("id")).first()
    
    if todo_model:
        return todo_model
    
    raise HTTPException(status_code=404, detail="Todo not found!")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: Annotated[Session, Depends(get_db)], todo_request: TodoRequest):
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    todo_model = Todos(**todo_request.model_dump(), user_id=user.get('id'))
    
    db.add(todo_model)
    db.commit()
    

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: Annotated[Session, Depends(get_db)],
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0)
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.user_id == user.get('id')).first()
    
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found!")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: Annotated[Session, Depends(get_db)], todo_id: int=Path(gt=0)):
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.user_id == user.get('id')).first()
    
    if not todo_model:
        raise HTTPException(status_code=404, detail='Todo not found!')
    
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.user_id == user.get('id')).delete()
    db.commit()  