"""
РОУТЕР ДЛЯ АУТЕНТИФИКАЦИИ
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import uuid
import sys
import os

# Добавляем корень проекта в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Импортируем из корневого config.py
from config import get_db, User, RefreshToken
from .. import schemas
from ..auth_logic import (
    authenticate_user, create_access_token, create_refresh_token,
    save_refresh_token, verify_refresh_token, get_password_hash,
    verify_password
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    try:
        print(f"📝 Регистрация пользователя: {user_data.email}")
        
        # Проверяем email
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            print(f"❌ Email уже зарегистрирован: {user_data.email}")
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Проверяем username если указан
        if user_data.username:
            existing_user = db.query(User).filter(User.username == user_data.username).first()
            if existing_user:
                print(f"❌ Username уже занят: {user_data.username}")
                raise HTTPException(
                    status_code=400,
                    detail="Username already taken"
                )
        
        # Создаем пользователя
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            password_hash=get_password_hash(user_data.password)
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"✅ Пользователь создан: {db_user.id_user}")
        
        # Возвращаем как словарь
        return {
            "id_user": db_user.id_user,
            "email": db_user.email,
            "username": db_user.username,
            "full_name": db_user.full_name,
            "is_active": bool(db_user.is_active),
            "is_verified": bool(db_user.is_verified),
            "last_login_at": db_user.last_login_at,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at
        }
        
    except IntegrityError as e:
        # Обработка ошибок уникальности из базы данных
        db.rollback()
        error_msg = str(e.orig)
        
        if "users_email_key" in error_msg or "email" in error_msg.lower():
            detail = "Email already registered"
        elif "users_username_key" in error_msg or "username" in error_msg.lower():
            detail = "Username already taken"
        else:
            detail = "Duplicate key violation"
            
        print(f"❌ Ошибка уникальности: {detail}")
        raise HTTPException(
            status_code=400,
            detail=detail
        )
        
    except HTTPException:
        # Перевыбрасываем HTTP исключения
        raise
        
    except Exception as e:
        # Любая другая ошибка
        db.rollback()
        print(f"❌ Неожиданная ошибка: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Вход пользователя"""
    # Аутентифицируем
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Обновляем время входа
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Создаем токены
    access_token = create_access_token(user.id_user, user.email)
    refresh_token = create_refresh_token(user.id_user, user.email)
    
    # Сохраняем refresh токен
    device_info = request.headers.get("User-Agent", "") if request else ""
    ip_address = request.client.host if request and request.client else None
    
    save_refresh_token(
        db=db,
        user_id=user.id_user,
        refresh_token=refresh_token,
        device_info=device_info[:500],
        ip_address=ip_address
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# ... остальной код без изменений

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    token_data: schemas.RefreshTokenRequest,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Обновление access токена"""
    from ..auth_logic import verify_token
    from ..crud import get_user_by_id
    
    try:
        # Проверяем refresh токен
        payload = verify_token(token_data.refresh_token, "refresh")
        user_id = uuid.UUID(payload.get("sub"))
        
        # Проверяем, существует ли токен в базе
        if not verify_refresh_token(db, token_data.refresh_token, user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Получаем пользователя
        user = get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Создаем новые токены
        new_access_token = create_access_token(user.id_user, user.email)
        new_refresh_token = create_refresh_token(user.id_user, user.email)
        
        # Обновляем refresh токен в базе
        device_info = request.headers.get("User-Agent", "") if request else ""
        ip_address = request.client.host if request and request.client else None
        
        save_refresh_token(
            db=db,
            user_id=user.id_user,
            refresh_token=new_refresh_token,
            device_info=device_info[:500],
            ip_address=ip_address
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/logout")
async def logout(
    token_data: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Выход пользователя"""
    from ..auth_logic import verify_token
    
    try:
        # Проверяем токен
        payload = verify_token(token_data.refresh_token, "refresh")
        user_id = uuid.UUID(payload.get("sub"))
        
        # Удаляем токен из базы
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).delete()
        db.commit()
        
        return {"message": "Successfully logged out"}
    except:
        # Даже если токен невалидный, считаем выход успешным
        return {"message": "Successfully logged out"}