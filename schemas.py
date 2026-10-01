from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UsuarioBase(BaseModel):
    name: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioOut(UsuarioBase):
    id: int

    class Config:
        from_attributes = True

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: str
    thumbnail_url: Optional[str] = None

class VideoCreate(VideoBase):
    user_id: int

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class VideoOut(VideoBase):
    id: int
    views: int
    user_id: int

    class Config:
        from_attributes = True

# --- schemas de Comentario ---
class ComentarioBase(BaseModel):
    content: str

class ComentarioCreate(ComentarioBase):
    user_id: int

class ComentarioOut(ComentarioBase):
    id: int
    user_id: int
    video_id: int
    created_at: datetime

    class Config:
        from_attributes = True
