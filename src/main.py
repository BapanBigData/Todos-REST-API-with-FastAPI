from fastapi import FastAPI
from src.database.database import init_db
from src.routers.auth import router as auth_router
from src.routers.todos import router as todos_router 
from src.routers.admin import router as admin_router
from src.routers.users import router as users_router



app = FastAPI()


# Create DB tables at app startup
init_db()

app.include_router(auth_router)
app.include_router(todos_router)
app.include_router(admin_router)
app.include_router(users_router)
