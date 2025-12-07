from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from src.core.database import get_db
from src.api.dependencies import get_current_user
from src.services.user.service import UserService
from src.schemas.user import (
    UserResponse, UserPublicResponse, UsersListResponse,
    UserUpdate, UserProfileUpdate, PasswordChange, EmailUpdate
)
from src.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить свой профиль"""
    user_service = UserService(db)
    return await user_service.get_current_user(current_user.id_user)

@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Получить публичный профиль пользователя"""
    user_service = UserService(db)
    return await user_service.get_user_profile(user_id)

@router.get("/", response_model=UsersListResponse)
async def get_users_list(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Number of records to return"),
    only_active: bool = Query(True, description="Show only active users"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список пользователей"""
    user_service = UserService(db)
    return await user_service.get_users_list(skip, limit, only_active)

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить свой профиль"""
    user_service = UserService(db)
    return await user_service.update_user_profile(current_user.id_user, profile_data)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить пользователя (админ или владелец)"""
    # TODO: Добавить проверку прав (админ или владелец)
    user_service = UserService(db)
    return await user_service.update_user(user_id, update_data)

@router.post("/me/change-password")
async def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Сменить пароль"""
    user_service = UserService(db)
    return await user_service.change_password(current_user.id_user, password_data)

@router.post("/me/update-email")
async def update_my_email(
    email_data: EmailUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить email"""
    user_service = UserService(db)
    return await user_service.update_email(current_user.id_user, email_data)

@router.post("/me/deactivate")
async def deactivate_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Деактивировать свой аккаунт"""
    user_service = UserService(db)
    return await user_service.deactivate_account(current_user.id_user, current_user.id_user)

@router.delete("/me")
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить свой аккаунт"""
    user_service = UserService(db)
    return await user_service.delete_account(current_user.id_user, current_user.id_user)

@router.get("/search/")
async def search_users(
    query: str = Query(..., min_length=2, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Поиск пользователей"""
    user_service = UserService(db)
    users = await user_service.search_users(query, skip, limit)
    return {"query": query, "results": users, "count": len(users)}