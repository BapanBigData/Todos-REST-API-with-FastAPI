from fastapi import FastAPI
from starlette import status


app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"msg": "Hello, World!"}

