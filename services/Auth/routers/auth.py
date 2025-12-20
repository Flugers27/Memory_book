"""
РОУТЕР ДЛЯ АУТЕНТИФИКАЦИИ
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

from database.session import get_db

from services.Auth.models import User, RefreshToken, UserRole
from services.Auth import schemas
from ..utils import send_verification_email
from services.Auth.auth_logic import (
    create_verification_token, verify_verification_token,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    save_refresh_token,
    verify_refresh_token,
    verify_token,
    get_password_hash
)
from services.Auth.crud import get_user_by_id, create_user

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    try:
        print(f"📝 Регистрация пользователя: {user_data.email}")

        # Получаем роль по умолчанию
        default_role = db.query(UserRole).filter(UserRole.role_name == "user").first()
        if not default_role:
            raise HTTPException(status_code=500, detail="Default role not found")

        # Создаем пользователя с ролью по умолчанию
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            password_hash=get_password_hash(user_data.password),
            is_active=True,
            is_verified=False,
            role_id=default_role.id_role
        )
        print("@@#@4")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Создаем JWT для верификации
        # verification_token = create_verification_token(db_user.id_user)
        # background_tasks.add_task(send_verification_email, db_user.email, verification_token)

        return schemas.UserResponse.from_orm(db_user)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig).lower() if e.orig else ""
        if "email" in error:
            detail = "Email already registered"
        elif "username" in error:
            detail = "Username already taken"
        else:
            detail = "User already exists"
        raise HTTPException(status_code=400, detail=detail)

    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Вход пользователя"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Обновляем время входа
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
        device_info=device_info[:500] if device_info else None,
        ip_address=ip_address
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    token_data: schemas.RefreshTokenRequest,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Обновление access токена"""
    try:
        payload = verify_token(token_data.refresh_token, "refresh")
        user_id = uuid.UUID(payload.get("sub"))

        if not verify_refresh_token(db, token_data.refresh_token, user_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")

        new_access_token = create_access_token(user.id_user, user.email)
        new_refresh_token = create_refresh_token(user.id_user, user.email)

        device_info = request.headers.get("User-Agent", "") if request else ""
        ip_address = request.client.host if request and request.client else None

        save_refresh_token(
            db=db,
            user_id=user.id_user,
            refresh_token=new_refresh_token,
            device_info=device_info[:500] if device_info else None,
            ip_address=ip_address
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка обновления токена: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not refresh token")


@router.post("/logout")
async def logout(
    token_data: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Выход пользователя"""
    try:
        payload = verify_token(token_data.refresh_token, "refresh")
        user_id = uuid.UUID(payload.get("sub"))

        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        db.commit()
        return {"message": "Successfully logged out"}

    except HTTPException:
        return {"message": "Successfully logged out"}
    except Exception as e:
        print(f"⚠️ Ошибка при выходе: {str(e)}")
        return {"message": "Successfully logged out"}


@router.post("/validate", response_model=schemas.TokenValidationResponse)
async def validate_token(token: str = None):
    """Валидация токена (для внутреннего использования)"""
    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required")

        payload = verify_token(token, "access")
        return schemas.TokenValidationResponse(
            valid=True,
            user_id=str(payload.get("sub")),
            email=payload.get("email"),
            expires_at=payload.get("exp")
        )

    except HTTPException as e:
        return schemas.TokenValidationResponse(valid=False, error=e.detail)
    except Exception as e:
        return schemas.TokenValidationResponse(valid=False, error=str(e))
