"""
РОУТЕР ДЛЯ РАБОТЫ С ПРОФИЛЕМ ПОЛЬЗОВАТЕЛЯ.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

# Импортируем из общей базы данных
from database.session import get_db

# Импортируем из текущего сервиса
from ..models import User
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
    return {
        "id_user": current_user.id_user,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "last_login_at": current_user.last_login_at,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.put("/me", response_model=schemas.UserResponse)
async def update_user_info(
    user_data: schemas.UserBase,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление информации о пользователе"""
    try:
        # Проверяем уникальность email если он изменился
        if user_data.email and user_data.email != current_user.email:
            existing_user = db.query(User).filter(
                User.email == user_data.email,
                User.id_user != current_user.id_user
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Проверяем уникальность username если он изменился
        if user_data.username and user_data.username != current_user.username:
            existing_user = db.query(User).filter(
                User.username == user_data.username,
                User.id_user != current_user.id_user
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Обновляем поля
        for field, value in user_data.dict(exclude_unset=True).items():
            if value is not None and hasattr(current_user, field):
                setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "id_user": current_user.id_user,
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "last_login_at": current_user.last_login_at,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.put("/me/password", status_code=status.HTTP_200_OK)
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
    
    # Проверяем, что новый пароль отличается от старого
    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Обновляем пароль
    success = update_user_password(db, current_user.id_user, password_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"message": "Password updated successfully"}

@router.get("/me/tokens", status_code=status.HTTP_200_OK)
async def get_user_tokens(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение списка активных refresh токенов пользователя"""
    from ..models import RefreshToken
    from datetime import datetime
    
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id_user,
        RefreshToken.expires_at > datetime.utcnow()
    ).all()
    
    return {
        "tokens": [
            {
                "device_info": token.device_info,
                "ip_address": token.ip_address,
                "created_at": token.created_at.isoformat(),
                "expires_at": token.expires_at.isoformat()
            }
            for token in tokens
        ]
    }

@router.post("/me/tokens/revoke-all", status_code=status.HTTP_200_OK)
async def revoke_all_tokens(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Отзыв всех refresh токенов пользователя"""
    from ..models import RefreshToken
    
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id_user
    ).delete()
    
    db.commit()
    
    return {"message": "All refresh tokens revoked"}