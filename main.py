# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from typing import List

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Memory Book API"}

# CRUD операции для пользователей
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Здесь должна быть логика создания пользователя
    # Например, хеширование пароля и т.д.
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # В реальном приложении хешируй пароль!
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# CRUD операции для воспоминаний
@app.post("/memories/", response_model=schemas.Memory)
def create_memory(memory: schemas.MemoryCreate, user_id: int, db: Session = Depends(get_db)):
    db_memory = models.Memory(**memory.dict(), user_id=user_id)
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory

@app.get("/memories/", response_model=List[schemas.Memory])
def read_memories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    memories = db.query(models.Memory).offset(skip).limit(limit).all()
    return memories