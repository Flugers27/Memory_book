from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user_repository import UserRepository
from src.schemas.user import (
    UserUpdate, UserProfileUpdate, PasswordChange,
    EmailUpdate, UserResponse, UserPublicResponse, UsersListResponse
)
from src.core.security import SecurityManager

class UserService:
    """Сервис пользователей"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
    
    async def get_current_user(self, user_id: UUID) -> UserResponse:
        """Получение текущего пользователя"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.model_validate(user)
    
    async def get_user_profile(self, user_id: UUID) -> UserPublicResponse:
        """Получение публичного профиля пользователя"""
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserPublicResponse.model_validate(user)
    
    async def get_users_list(
        self,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = True
    ) -> UsersListResponse:
        """Получение списка пользователей"""
        users = await self.user_repo.get_all(skip, limit, only_active)
        total = await self.user_repo.count_all(only_active)
        
        return UsersListResponse(
            users=[UserPublicResponse.model_validate(user) for user in users],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def update_user_profile(
        self,
        user_id: UUID,
        profile_data: UserProfileUpdate
    ) -> UserResponse:
        """Обновление профиля пользователя"""
        update_data = profile_data.dict(exclude_unset=True)
        
        # Проверяем существование пользователя
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        updated_user = await self.user_repo.update(user_id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        
        await self.session.commit()
        return UserResponse.model_validate(updated_user)
    
    async def update_user(
        self,
        user_id: UUID,
        update_data: UserUpdate
    ) -> UserResponse:
        """Полное обновление пользователя (админ или владелец)"""
        update_dict = update_data.dict(exclude_unset=True)
        
        # Если обновляется username, проверяем уникальность
        if 'username' in update_dict and update_dict['username']:
            existing_user = await self.user_repo.get_by_username(update_dict['username'])
            if existing_user and existing_user.id_user != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        updated_user = await self.user_repo.update(user_id, update_dict)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await self.session.commit()
        return UserResponse.model_validate(updated_user)
    
    async def change_password(
        self,
        user_id: UUID,
        password_data: PasswordChange
    ) -> dict:
        """Смена пароля"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Проверяем текущий пароль
        if not SecurityManager.verify_password(
            password_data.current_password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Обновляем пароль
        await self.user_repo.update(user_id, {
            "password_hash": SecurityManager.get_password_hash(password_data.new_password)
        })
        
        await self.session.commit()
        return {"message": "Password changed successfully"}
    
    async def update_email(
        self,
        user_id: UUID,
        email_data: EmailUpdate
    ) -> dict:
        """Обновление email"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Проверяем текущий пароль
        if not SecurityManager.verify_password(
            email_data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )
        
        # Проверяем, не занят ли новый email
        existing_user = await self.user_repo.get_by_email(email_data.new_email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        
        # Обновляем email
        await self.user_repo.update(user_id, {"email": email_data.new_email})
        
        await self.session.commit()
        return {"message": "Email updated successfully"}
    
    async def deactivate_account(self, user_id: UUID, current_user_id: UUID) -> dict:
        """Деактивация аккаунта"""
        # Проверяем права
        if user_id != current_user_id:
            # TODO: Проверка на администратора
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        success = await self.user_repo.deactivate(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await self.session.commit()
        return {"message": "Account deactivated successfully"}
    
    async def delete_account(self, user_id: UUID, current_user_id: UUID) -> dict:
        """Удаление аккаунта"""
        # Проверяем права
        if user_id != current_user_id:
            # TODO: Проверка на администратора
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        success = await self.user_repo.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await self.session.commit()
        return {"message": "Account deleted successfully"}
    
    async def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[UserPublicResponse]:
        """Поиск пользователей"""
        # TODO: Реализовать полнотекстовый поиск
        # Временная реализация - поиск по username и email
        from sqlalchemy import or_
        from sqlalchemy import select
        
        stmt = select(self.user_repo.model).where(
            or_(
                self.user_repo.model.username.ilike(f"%{query}%"),
                self.user_repo.model.email.ilike(f"%{query}%"),
                self.user_repo.model.full_name.ilike(f"%{query}%")
            ),
            self.user_repo.model.is_active == True
        ).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        
        return [UserPublicResponse.model_validate(user) for user in users]