from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user_repository import UserRepository
from src.repositories.token_repository import TokenRepository
from src.schemas.user import UserCreate, UserLogin
from src.schemas.token import TokenPair
from src.core.security import SecurityManager

class AuthService:
    """Сервис аутентификации"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = TokenRepository(session)
    
    async def register(self, user_data: UserCreate) -> Tuple[dict, str]:
        """Регистрация нового пользователя"""
        # Проверяем существование пользователя
        if await self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        if user_data.username and await self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Создаем пользователя
        user = await self.user_repo.create({
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "password_hash": SecurityManager.get_password_hash(user_data.password)
        })
        
        await self.session.commit()
        
        # Генерируем токен верификации (упрощенно)
        verification_token = "temp_verification_token"
        
        return {
            "id_user": user.id_user,
            "email": user.email,
            "username": user.username
        }, verification_token
    
    async def login(
        self,
        login_data: UserLogin,
        request: Request,
        user_agent: Optional[str] = None
    ) -> Tuple[dict, TokenPair]:
        """Вход в систему"""
        # Ищем пользователя
        user = await self.user_repo.get_by_email(login_data.email)
        if not user or not SecurityManager.verify_password(
            login_data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated"
            )
        
        # Обновляем время последнего входа
        await self.user_repo.update_last_login(user.id_user)
        
        # Создаем токены
        access_token = SecurityManager.create_access_token({
            "sub": str(user.id_user),
            "email": user.email,
            "username": user.username
        })
        
        refresh_token = SecurityManager.create_refresh_token(
            user.id_user,
            user.email
        )
        
        # Сохраняем refresh токен
        await self.token_repo.create({
            "user_id": user.id_user,
            "token_hash": SecurityManager.hash_token(refresh_token),
            "device_info": user_agent,
            "ip_address": request.client.host if request.client else None,
            "expires_at": datetime.utcnow()
        })
        
        await self.session.commit()
        
        user_data = {
            "id_user": user.id_user,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "is_verified": user.is_verified
        }
        
        return user_data, TokenPair(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    async def refresh_tokens(self, refresh_token: str, request: Request) -> TokenPair:
        """Обновление токенов"""
        # Проверяем токен
        payload = SecurityManager.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = UUID(payload.get("sub"))
        token_hash = SecurityManager.hash_token(refresh_token)
        
        # Проверяем наличие токена в БД
        token = await self.token_repo.get_by_hash(token_hash)
        if not token or token.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Получаем пользователя
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Удаляем старый токен
        await self.token_repo.delete(token.id_user_token)
        
        # Создаем новые токены
        new_access_token = SecurityManager.create_access_token({
            "sub": str(user.id_user),
            "email": user.email,
            "username": user.username
        })
        
        new_refresh_token = SecurityManager.create_refresh_token(
            user.id_user,
            user.email
        )
        
        # Сохраняем новый токен
        await self.token_repo.create({
            "user_id": user.id_user,
            "token_hash": SecurityManager.hash_token(new_refresh_token),
            "device_info": token.device_info,
            "ip_address": request.client.host if request.client else None,
            "expires_at": datetime.utcnow()
        })
        
        await self.session.commit()
        
        return TokenPair(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    
    async def logout(self, refresh_token: str) -> None:
        """Выход из системы"""
        payload = SecurityManager.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return
        
        token_hash = SecurityManager.hash_token(refresh_token)
        await self.token_repo.delete_by_hash(token_hash)
        await self.session.commit()
    
    async def logout_all(self, user_id: UUID) -> None:
        """Выход из всех устройств"""
        await self.token_repo.delete_all_by_user(user_id)
        await self.session.commit()