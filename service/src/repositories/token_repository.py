from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from src.models.token import RefreshToken

class TokenRepository:
    """Репозиторий для работы с токенами"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, token_data: dict) -> RefreshToken:
        """Создание refresh токена"""
        token = RefreshToken(**token_data)
        self.session.add(token)
        await self.session.flush()
        return token
    
    async def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Получение токена по хэшу"""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_and_device(
        self,
        user_id: UUID,
        device_info: str
    ) -> Optional[RefreshToken]:
        """Получение токена по пользователю и устройству"""
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.device_info == device_info
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_user(self, user_id: UUID) -> List[RefreshToken]:
        """Получение всех токенов пользователя"""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return list(result.scalars().all())
    
    async def delete(self, token_id: UUID) -> bool:
        """Удаление токена"""
        token = await self.session.get(RefreshToken, token_id)
        if not token:
            return False
        
        await self.session.delete(token)
        await self.session.flush()
        return True
    
    async def delete_by_hash(self, token_hash: str) -> bool:
        """Удаление токена по хэшу"""
        token = await self.get_by_hash(token_hash)
        if not token:
            return False
        
        await self.session.delete(token)
        await self.session.flush()
        return True
    
    async def delete_expired(self) -> int:
        """Удаление просроченных токенов"""
        result = await self.session.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
        )
        return result.rowcount
    
    async def delete_all_by_user(self, user_id: UUID) -> int:
        """Удаление всех токенов пользователя"""
        result = await self.session.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return result.rowcount