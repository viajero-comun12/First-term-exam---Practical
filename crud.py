from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()

def create_user(db: Session, user: schemas.UsuarioCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.Usuario(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, login_data: schemas.UsuarioLogin):
    user = get_user_by_email(db, login_data.email)
    if not user:
        return False
    if not verify_password(login_data.password, user.password_hash):
        return False
    return user

def get_videos(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    query = db.query(models.Video)
    if user_id is not None:
        query = query.filter(models.Video.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def get_video(db: Session, video_id: int):
    return db.query(models.Video).filter(models.Video.id == video_id).first()

def create_video(db: Session, video: schemas.VideoCreate):
    db_video = models.Video(**video.model_dump())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def update_video(db: Session, video_id: int, video: schemas.VideoUpdate):
    db_video = get_video(db, video_id)
    if not db_video:
        return None
    
    update_data = video.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_video, key, value)
        
    db.commit()
    db.refresh(db_video)
    return db_video

def delete_video(db: Session, video_id: int):
    db_video = get_video(db, video_id)
    if db_video:
        db.delete(db_video)
        db.commit()
        return True
    return False

def get_comments_by_video(db: Session, video_id: int):
    return db.query(models.Comentario).filter(models.Comentario.video_id == video_id).all()

def create_comment(db: Session, video_id: int, comment: schemas.ComentarioCreate):
    db_comment = models.Comentario(
        content=comment.content,
        user_id=comment.user_id,
        video_id=video_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
