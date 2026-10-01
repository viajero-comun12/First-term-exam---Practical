from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile, Form
import uuid
from s3 import upload_file_to_s3, S3_BUCKET_VIDEOS, S3_BUCKET_THUMBNAILS


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Video Streaming API",
    description="API para subir y visualizar videos (evaluación).",
    version="1.0.0",
    docs_url="/docs" 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return crud.create_user(db=db, user=user)

@app.post("/login")
def login(login_data: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    return {"message": "Login exitoso", "user_id": user.id, "email": user.email}

@app.get("/users/{user_id}", response_model=schemas.UsuarioOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user


@app.post("/videos", response_model=schemas.VideoOut, status_code=status.HTTP_201_CREATED)
def create_video(
    title: str = Form(...),
    description: str = Form(None),
    user_id: int = Form(...),
    video_file: UploadFile = File(...),
    thumbnail_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    video_ext = video_file.filename.split('.')[-1]
    video_obj_name = f"{uuid.uuid4()}.{video_ext}"
    video_url = upload_file_to_s3(video_file.file, video_obj_name, video_file.content_type, S3_BUCKET_VIDEOS)
    
    if not video_url:
        raise HTTPException(status_code=500, detail="Error uploading video to S3")
        
    thumbnail_url = None
    if thumbnail_file:
        thumb_ext = thumbnail_file.filename.split('.')[-1]
        thumb_obj_name = f"{uuid.uuid4()}.{thumb_ext}"
        thumbnail_url = upload_file_to_s3(thumbnail_file.file, thumb_obj_name, thumbnail_file.content_type, S3_BUCKET_THUMBNAILS)
        
    video_data = schemas.VideoCreate(
        title=title,
        description=description,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        user_id=user_id
    )
    return crud.create_video(db=db, video=video_data)

@app.get("/videos", response_model=List[schemas.VideoOut])
def read_videos(skip: int = 0, limit: int = 100, user_id: int = None, db: Session = Depends(get_db)):
    videos = crud.get_videos(db, skip=skip, limit=limit, user_id=user_id)
    return videos

@app.get("/videos/{video_id}", response_model=schemas.VideoOut)
def read_video(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return db_video

@app.put("/videos/{video_id}", response_model=schemas.VideoOut)
def update_video(video_id: int, video: schemas.VideoUpdate, db: Session = Depends(get_db)):
    db_video = crud.update_video(db, video_id, video)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return db_video

@app.delete("/videos/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)):
    success = crud.delete_video(db, video_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return {"message": "Video eliminado correctamente"}


@app.post("/videos/{video_id}/comments", response_model=schemas.ComentarioOut, status_code=status.HTTP_201_CREATED)
def create_comment_for_video(video_id: int, comment: schemas.ComentarioCreate, db: Session = Depends(get_db)):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return crud.create_comment(db=db, video_id=video_id, comment=comment)

@app.get("/videos/{video_id}/comments", response_model=List[schemas.ComentarioOut])
def read_comments_for_video(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    comments = crud.get_comments_by_video(db, video_id=video_id)
    return comments
