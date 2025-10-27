from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, Enum, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class People(db.Model):
    __tablename__ = 'people'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    height: Mapped[str | None] = mapped_column(String(20), nullable=True)
    mass: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hair_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    eye_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    birth_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Planet(db.Model):
    __tablename__ = 'planets'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    diameter: Mapped[str | None] = mapped_column(String(50), nullable=True)
    climate: Mapped[str | None] = mapped_column(String(100), nullable=True)
    terrain: Mapped[str | None] = mapped_column(String(100), nullable=True)
    population: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    favorite_type: Mapped[str] = mapped_column(Enum('people', 'planet', name='favorite_types'), nullable=False)
    favorite_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    user: Mapped["User"] = relationship(back_populates="favorites")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'favorite_type', 'favorite_id', name='unique_favorite'),
    )
    
    def serialize(self):
        favorite_name = None
        if self.favorite_type == 'people':
            person = db.session.get(People, self.favorite_id)
            favorite_name = person.name if person else None
        elif self.favorite_type == 'planet':
            planet = db.session.get(Planet, self.favorite_id)
            favorite_name = planet.name if planet else None
        
        return {
            "id": self.id,
            "user_id": self.user_id,
            "favorite_type": self.favorite_type,
            "favorite_id": self.favorite_id,
            "favorite_name": favorite_name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }