from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))

    videos = relationship("Video", back_populates="owner")
    comentarios = relationship("Comentario", back_populates="owner")

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    video_url = Column(String(500))
    thumbnail_url = Column(String(500), nullable=True)
    views = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("usuarios.id"))

    owner = relationship("Usuario", back_populates="videos")
    comentarios = relationship("Comentario", back_populates="video")

class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("Usuario", back_populates="comentarios")
    video = relationship("Video", back_populates="comentarios")
