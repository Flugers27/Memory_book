"""
CRUD операции для сервиса Family Tree
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional, List, Tuple
from datetime import datetime, timezone
import uuid
import logging

from database.models.family import FamilyTree, FamilyTreeAgent, RelationshipAgent
from . import schemas

logger = logging.getLogger(__name__)


# ========== Family Tree CRUD ==========

def create_family_tree(
    db: Session,
    tree_data: schemas.FamilyTreeCreate,
    user_id: uuid.UUID
) -> FamilyTree:
    """Создаёт новое семейное древо"""
    db_tree = FamilyTree(
        name_family_tree=tree_data.name_family_tree,
        is_public=tree_data.is_public,
        is_draft=tree_data.is_draft,
        user_id=user_id
    )
    db.add(db_tree)
    db.commit()
    db.refresh(db_tree)
    logger.info(f"Created family tree {db_tree.id_family_tree} for user {user_id}")
    return db_tree


def get_user_trees(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[FamilyTree], int]:
    """Получает список древ пользователя с пагинацией"""
    query = db.query(FamilyTree).filter(FamilyTree.user_id == user_id)
    total = query.count()
    trees = query.order_by(desc(FamilyTree.updated_at)).offset(skip).limit(limit).all()
    return trees, total


def get_user_tree_by_id(
    db: Session,
    tree_id: uuid.UUID,
    user_id: uuid.UUID
) -> Optional[FamilyTree]:
    """Получает конкретное древо пользователя"""
    return db.query(FamilyTree).filter(
        FamilyTree.id_family_tree == tree_id,
        FamilyTree.user_id == user_id
    ).first()


def get_tree_by_id(
    db: Session,
    tree_id: uuid.UUID
) -> Optional[FamilyTree]:
    """Получает древо по ID (без проверки владельца)"""
    return db.query(FamilyTree).filter(
        FamilyTree.id_family_tree == tree_id
    ).first()


def update_family_tree(
    db: Session,
    tree_id: uuid.UUID,
    user_id: uuid.UUID,
    update_data: schemas.FamilyTreeUpdate
) -> Optional[FamilyTree]:
    """Обновляет древо"""
    db_tree = get_user_tree_by_id(db, tree_id, user_id)
    if not db_tree:
        return None
    
    update_values = update_data.dict(exclude_unset=True)
    for field, value in update_values.items():
        if value is not None:
            setattr(db_tree, field, value)
    
    db_tree.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_tree)
    logger.info(f"Updated family tree {tree_id}")
    return db_tree


def delete_family_tree(
    db: Session,
    tree_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """Удаляет древо (каскадно удаляет связи и привязки агентов)"""
    db_tree = get_user_tree_by_id(db, tree_id, user_id)
    if not db_tree:
        return False
    
    db.delete(db_tree)
    db.commit()
    logger.info(f"Deleted family tree {tree_id}")
    return True


# ========== Public Trees ==========

def get_public_trees(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[FamilyTree], int]:
    """Получает список публичных древ"""
    query = db.query(FamilyTree).filter(
        FamilyTree.is_public == True,
        FamilyTree.is_draft == False
    )
    total = query.count()
    trees = query.order_by(desc(FamilyTree.updated_at)).offset(skip).limit(limit).all()
    return trees, total


def get_public_tree_by_id(
    db: Session,
    tree_id: uuid.UUID
) -> Optional[FamilyTree]:
    """Получает конкретное публичное древо"""
    return db.query(FamilyTree).filter(
        FamilyTree.id_family_tree == tree_id,
        FamilyTree.is_public == True,
        FamilyTree.is_draft == False
    ).first()


# ========== Family Tree Agents CRUD ==========

def add_agent_to_tree(
    db: Session,
    tree_id: uuid.UUID,
    agent_id: uuid.UUID
) -> Optional[FamilyTreeAgent]:
    """Добавляет агента в древо"""
    # Проверяем, не добавлен ли уже агент
    existing = db.query(FamilyTreeAgent).filter(
        FamilyTreeAgent.family_tree_id == tree_id,
        FamilyTreeAgent.agent_id == agent_id
    ).first()
    if existing:
        return existing
    
    db_agent = FamilyTreeAgent(
        family_tree_id=tree_id,
        agent_id=agent_id
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    logger.info(f"Added agent {agent_id} to tree {tree_id}")
    return db_agent


def remove_agent_from_tree(
    db: Session,
    tree_id: uuid.UUID,
    agent_id: uuid.UUID
) -> bool:
    """Удаляет агента из древа"""
    db_agent = db.query(FamilyTreeAgent).filter(
        FamilyTreeAgent.family_tree_id == tree_id,
        FamilyTreeAgent.agent_id == agent_id
    ).first()
    if not db_agent:
        return False
    
    db.delete(db_agent)
    db.commit()
    logger.info(f"Removed agent {agent_id} from tree {tree_id}")
    return True


def get_tree_agents(
    db: Session,
    tree_id: uuid.UUID
) -> List[FamilyTreeAgent]:
    """Получает список агентов в древе"""
    return db.query(FamilyTreeAgent).filter(
        FamilyTreeAgent.family_tree_id == tree_id
    ).all()


# ========== Relationships CRUD ==========

def create_relationship(
    db: Session,
    tree_id: uuid.UUID,
    user_id: uuid.UUID,
    rel_data: schemas.RelationshipCreate
) -> Optional[RelationshipAgent]:
    """Создаёт родственную связь между агентами"""
    db_rel = RelationshipAgent(
        type_relative=rel_data.type_relative,
        is_blood_relative=rel_data.is_blood_relative,
        agent_from=rel_data.agent_from,
        agent_to=rel_data.agent_to,
        family_tree_id=tree_id,
        user_id=user_id
    )
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    logger.info(f"Created relationship {db_rel.id_relationships} in tree {tree_id}")
    return db_rel


def get_tree_relationships(
    db: Session,
    tree_id: uuid.UUID
) -> List[RelationshipAgent]:
    """Получает список связей в древе"""
    return db.query(RelationshipAgent).filter(
        RelationshipAgent.family_tree_id == tree_id
    ).all()


def get_relationship_by_id(
    db: Session,
    rel_id: uuid.UUID
) -> Optional[RelationshipAgent]:
    """Получает связь по ID"""
    return db.query(RelationshipAgent).filter(
        RelationshipAgent.id_relationships == rel_id
    ).first()


def update_relationship(
    db: Session,
    rel_id: uuid.UUID,
    update_data: schemas.RelationshipUpdate
) -> Optional[RelationshipAgent]:
    """Обновляет родственную связь"""
    db_rel = get_relationship_by_id(db, rel_id)
    if not db_rel:
        return None
    
    update_values = update_data.dict(exclude_unset=True)
    for field, value in update_values.items():
        if value is not None:
            setattr(db_rel, field, value)
    
    db_rel.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_rel)
    logger.info(f"Updated relationship {rel_id}")
    return db_rel


def delete_relationship(
    db: Session,
    rel_id: uuid.UUID
) -> bool:
    """Удаляет родственную связь"""
    db_rel = get_relationship_by_id(db, rel_id)
    if not db_rel:
        return False
    
    db.delete(db_rel)
    db.commit()
    logger.info(f"Deleted relationship {rel_id}")
    return True