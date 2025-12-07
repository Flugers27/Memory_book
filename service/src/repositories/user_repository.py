from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from src.models.user import User

class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user_data: dict) -> User:
        """Создание пользователя"""
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id_user == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = True
    ) -> List[User]:
        """Получение списка пользователей"""
        query = select(User)
        
        if only_active:
            query = query.where(User.is_active == True)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_all(self, only_active: bool = True) -> int:
        """Подсчет общего количества пользователей"""
        query = select(User)
        
        if only_active:
            query = query.where(User.is_active == True)
        
        result = await self.session.execute(query)
        return len(result.scalars().all())
    
    async def update(self, user_id: UUID, update_data: dict) -> Optional[User]:
        """Обновление пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        await self.session.flush()
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """Удаление пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        await self.session.delete(user)
        await self.session.flush()
        return True
    
    async def deactivate(self, user_id: UUID) -> bool:
        """Деактивация пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await self.session.flush()
        return True
    
    async def update_last_login(self, user_id: UUID) -> bool:
        """Обновление времени последнего входа"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.last_login_at = datetime.utcnow()
        await self.session.flush()
        return True