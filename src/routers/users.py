from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from src.utility.db_utils import get_db
from src.database.models import Todos
from src.routers.auth import get_current_user


