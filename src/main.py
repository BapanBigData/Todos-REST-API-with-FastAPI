from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from src.database.database import init_db, SessionLocal
from src.database.models import Todos
from src.models.todos import TodoRequest


app = FastAPI()


# Create DB tables at app startup
init_db()


def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()



@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"msg": "Hello, World!"}


@app.get("/read_all", status_code=status.HTTP_200_OK)
async def read_all(db: Annotated[Session, Depends(get_db)]):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: Annotated[Session, Depends(get_db)], todo_id: int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if todo_model:
        return todo_model
    
    raise HTTPException(status_code=404, detail="Todo not found!")


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: Annotated[Session, Depends(get_db)], todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    
    db.add(todo_model)
    db.commit()
    

@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: Annotated[Session, Depends(get_db)],
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0)
):
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found!")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    
    db.add(todo_model)
    db.commit()


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: Annotated[Session, Depends(get_db)], todo_id: int=Path(gt=0)):
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if not todo_model:
        raise HTTPException(status_code=404, detail='Todo not found!')
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()     