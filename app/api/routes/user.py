from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, get_users
from app.core.security import require_admin

router = APIRouter()


@router.post("/", response_model=UserResponse)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user.name, user.email, user.password, user.role)


@router.get("/", response_model=list[UserResponse])
def get_users_route(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    return get_users(db)
