from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.auth.service import AuthService
from src.schemas.user import UserCreate, UserLogin
from src.schemas.token import TokenPair, RefreshTokenRequest
from src.api.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    auth_service = AuthService(db)
    user, verification_token = await auth_service.register(user_data)
    
    # TODO: Отправка email с верификацией
    
    return {
        "message": "User registered successfully",
        "user": user,
        "verification_sent": True
    }

@router.post("/login", response_model=TokenPair)
async def login(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_agent: str = None
):
    """Вход в систему"""
    auth_service = AuthService(db)
    user, tokens = await auth_service.login(login_data, request, user_agent)
    
    return tokens

@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
    token_data: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Обновление токенов"""
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(token_data.refresh_token, request)

@router.post("/logout")
async def logout(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Выход из системы"""
    auth_service = AuthService(db)
    await auth_service.logout(token_data.refresh_token)
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Выход из всех устройств"""
    auth_service = AuthService(db)
    await auth_service.logout_all(current_user.id_user)
    return {"message": "Logged out from all devices"}