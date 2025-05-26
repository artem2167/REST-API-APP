from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from .database import SessionLocal  # <— только импортим SessionLocal

# SQLAlchemy setup
#DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
#engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Статический API-ключ
API_KEY = os.getenv("API_KEY", "supersecret")

def get_db() -> Session:
    """
    Зависимость для получения сессии БД.
    В конце работы сессия закрывается.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(x_api_key: str = Header(...)):
    """
    Проверка наличия и корректности заголовка X-API-KEY.
    """
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "API key"},
        )
