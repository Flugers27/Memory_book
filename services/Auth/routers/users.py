"""
РОУТЕР ДЛЯ РАБОТЫ С ПРОФИЛЕМ ПОЛЬЗОВАТЕЛЯ.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys
import os

# Добавляем корень проекта в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import get_db, User
from .. import schemas
from ..dependencies import get_current_active_user
from ..auth_logic import verify_password
from ..crud import update_user_password

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации о текущем пользователе"""
    return current_user

@router.put("/me/password")
async def update_password(
    password_data: schemas.PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление пароля текущего пользователя"""
    # Проверяем текущий пароль
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Обновляем пароль
    success = update_user_password(db, current_user.id_user, password_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"message": "Password updated successfully"}