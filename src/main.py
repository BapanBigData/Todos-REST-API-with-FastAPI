from fastapi import FastAPI
from starlette import status
from src.database.database import init_db


app = FastAPI()


# Create DB tables at app startup
init_db()



@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"msg": "Hello, World!"}

