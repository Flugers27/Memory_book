"""
РОУТЕР ДЛЯ РАБОТЫ С СЕМЕЙНЫМИ ДРЕВАМИ
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from database.session import get_db
from .. import schemas
from ..crud import (
    create_family_tree, get_user_trees, get_user_tree_by_id, get_tree_by_id,
    update_family_tree, delete_family_tree,
    get_public_trees, get_public_tree_by_id,
    add_agent_to_tree, remove_agent_from_tree, get_tree_agents,
    create_relationship, get_tree_relationships, get_relationship_by_id,
    update_relationship, delete_relationship
)
from ..dependencies import get_current_user_id, get_optional_user_id

router = APIRouter(prefix="/family", tags=["family"])


# ========== Управление древами ==========

@router.post("/tree", response_model=schemas.FamilyTreeResponse, status_code=status.HTTP_201_CREATED)
def create_tree(
    tree_data: schemas.FamilyTreeCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создать новое генеалогическое древо"""
    try:
        db_tree = create_family_tree(db=db, tree_data=tree_data, user_id=user_id)
        return schemas.FamilyTreeResponse.from_orm(db_tree)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create family tree: {str(e)}"
        )


@router.get("/tree/my", response_model=schemas.FamilyTreeListResponse)
def get_my_trees(
    skip: int = Query(0, ge=0, description="Смещение"),
    limit: int = Query(20, ge=1, le=100, description="Лимит"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Список древ текущего пользователя (с пагинацией)"""
    try:
        trees, total = get_user_trees(db=db, user_id=user_id, skip=skip, limit=limit)
        return schemas.FamilyTreeListResponse(
            trees=[schemas.FamilyTreeResponse.from_orm(t) for t in trees],
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trees: {str(e)}"
        )


# ========== Публичные древа ==========
# ВАЖНО: публичные эндпоинты ДО /tree/{tree_id}, чтобы FastAPI
# не сопоставил "public" с path-параметром {tree_id}

@router.get("/tree/public", response_model=schemas.PublicFamilyTreeListResponse)
def get_public_trees_list(
    skip: int = Query(0, ge=0, description="Смещение"),
    limit: int = Query(20, ge=1, le=100, description="Лимит"),
    db: Session = Depends(get_db)
):
    """Список публичных древ (для всех пользователей)"""
    try:
        trees, total = get_public_trees(db=db, skip=skip, limit=limit)
        return schemas.PublicFamilyTreeListResponse(
            trees=[schemas.PublicFamilyTreeResponse.from_orm(t) for t in trees],
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public trees: {str(e)}"
        )


@router.get("/tree/public/{tree_id}", response_model=schemas.PublicFamilyTreeFullResponse)
def get_public_tree(
    tree_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Просмотр конкретного публичного древа (для всех пользователей)"""
    try:
        db_tree = get_public_tree_by_id(db=db, tree_id=tree_id)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Public family tree not found"
            )
        
        agents = get_tree_agents(db=db, tree_id=tree_id)
        relationships = get_tree_relationships(db=db, tree_id=tree_id)
        
        return schemas.PublicFamilyTreeFullResponse(
            id_family_tree=db_tree.id_family_tree,
            name_family_tree=db_tree.name_family_tree,
            is_public=db_tree.is_public,
            is_draft=db_tree.is_draft,
            created_at=db_tree.created_at,
            updated_at=db_tree.updated_at,
            agents=[schemas.FamilyTreeAgentResponse.from_orm(a) for a in agents],
            relationships=[schemas.RelationshipResponse.from_orm(r) for r in relationships]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public tree: {str(e)}"
        )


# ========== Управление древами (защищённые) ==========

@router.get("/tree/{tree_id}", response_model=schemas.FamilyTreeFullResponse)
def get_tree(
    tree_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Просмотр конкретного древа пользователя (со всеми агентами и связями)"""
    try:
        db_tree = get_user_tree_by_id(db=db, tree_id=tree_id, user_id=user_id)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found"
            )
        
        agents = get_tree_agents(db=db, tree_id=tree_id)
        relationships = get_tree_relationships(db=db, tree_id=tree_id)
        
        return schemas.FamilyTreeFullResponse(
            id_family_tree=db_tree.id_family_tree,
            name_family_tree=db_tree.name_family_tree,
            is_public=db_tree.is_public,
            is_draft=db_tree.is_draft,
            user_id=db_tree.user_id,
            created_at=db_tree.created_at,
            updated_at=db_tree.updated_at,
            agents=[schemas.FamilyTreeAgentResponse.from_orm(a) for a in agents],
            relationships=[schemas.RelationshipResponse.from_orm(r) for r in relationships]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tree: {str(e)}"
        )


@router.put("/tree/{tree_id}", response_model=schemas.FamilyTreeResponse)
def update_tree(
    tree_id: uuid.UUID,
    update_data: schemas.FamilyTreeUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновить название и настройки древа"""
    try:
        db_tree = update_family_tree(db=db, tree_id=tree_id, user_id=user_id, update_data=update_data)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found or access denied"
            )
        return schemas.FamilyTreeResponse.from_orm(db_tree)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tree: {str(e)}"
        )


@router.delete("/tree/{tree_id}", response_model=schemas.DeleteResponse)
def delete_tree(
    tree_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удалить древо (каскадно удаляет связи и привязки агентов)"""
    try:
        success = delete_family_tree(db=db, tree_id=tree_id, user_id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found or access denied"
            )
        return schemas.DeleteResponse(message="Family tree deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tree: {str(e)}"
        )


# ========== Агенты в древе ==========

@router.post("/tree/{tree_id}/agent", response_model=schemas.FamilyTreeAgentResponse, status_code=status.HTTP_201_CREATED)
def add_agent(
    tree_id: uuid.UUID,
    request: schemas.AddAgentRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Добавить агента (члена семьи) в древо"""
    try:
        # Проверяем, что древо принадлежит пользователю
        db_tree = get_user_tree_by_id(db=db, tree_id=tree_id, user_id=user_id)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found or access denied"
            )
        
        db_agent = add_agent_to_tree(db=db, tree_id=tree_id, agent_id=request.agent_id)
        return schemas.FamilyTreeAgentResponse.from_orm(db_agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add agent to tree: {str(e)}"
        )


@router.delete("/tree/{tree_id}/agent/{agent_id}", response_model=schemas.DeleteResponse)
def remove_agent(
    tree_id: uuid.UUID,
    agent_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удалить агента из древа"""
    try:
        # Проверяем, что древо принадлежит пользователю
        db_tree = get_user_tree_by_id(db=db, tree_id=tree_id, user_id=user_id)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found or access denied"
            )
        
        success = remove_agent_from_tree(db=db, tree_id=tree_id, agent_id=agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found in this tree"
            )
        return schemas.DeleteResponse(message="Agent removed from tree successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove agent from tree: {str(e)}"
        )


# ========== Связи между агентами ==========

@router.get("/tree/{tree_id}/relationship", response_model=schemas.RelationshipListResponse)
def get_relationships(
    tree_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Список всех родственных связей в древе"""
    try:
        # Проверяем, что древо принадлежит пользователю
        db_tree = get_user_tree_by_id(db=db, tree_id=tree_id, user_id=user_id)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found or access denied"
            )
        
        relationships = get_tree_relationships(db=db, tree_id=tree_id)
        return schemas.RelationshipListResponse(
            relationships=[schemas.RelationshipResponse.from_orm(r) for r in relationships],
            total=len(relationships)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get relationships: {str(e)}"
        )


@router.post("/tree/{tree_id}/relationship", response_model=schemas.RelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship_endpoint(
    tree_id: uuid.UUID,
    rel_data: schemas.RelationshipCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создать родственную связь между двумя агентами"""
    try:
        # Проверяем, что древо принадлежит пользователю
        db_tree = get_user_tree_by_id(db=db, tree_id=tree_id, user_id=user_id)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found or access denied"
            )
        
        db_rel = create_relationship(db=db, tree_id=tree_id, user_id=user_id, rel_data=rel_data)
        return schemas.RelationshipResponse.from_orm(db_rel)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create relationship: {str(e)}"
        )


@router.put("/tree/{tree_id}/relationship/{rel_id}", response_model=schemas.RelationshipResponse)
def update_relationship_endpoint(
    tree_id: uuid.UUID,
    rel_id: uuid.UUID,
    update_data: schemas.RelationshipUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновить тип родства и параметры связи"""
    try:
        # Проверяем, что древо принадлежит пользователю
        db_tree = get_user_tree_by_id(db=db, tree_id=tree_id, user_id=user_id)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found or access denied"
            )
        
        db_rel = update_relationship(db=db, rel_id=rel_id, update_data=update_data)
        if not db_rel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relationship not found"
            )
        return schemas.RelationshipResponse.from_orm(db_rel)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update relationship: {str(e)}"
        )


@router.delete("/tree/{tree_id}/relationship/{rel_id}", response_model=schemas.DeleteResponse)
def delete_relationship_endpoint(
    tree_id: uuid.UUID,
    rel_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удалить родственную связь"""
    try:
        # Проверяем, что древо принадлежит пользователю
        db_tree = get_user_tree_by_id(db=db, tree_id=tree_id, user_id=user_id)
        if not db_tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family tree not found or access denied"
            )
        
        success = delete_relationship(db=db, rel_id=rel_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relationship not found"
            )
        return schemas.DeleteResponse(message="Relationship deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete relationship: {str(e)}"
        )