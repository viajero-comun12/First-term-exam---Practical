import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuramos la URL de la base de datos (por defecto SQLite para pruebas si no hay variables de entorno, 
# pero la idea es conectar a RDS MySQL o PostgreSQL)
# Ejemplo para PostgreSQL en RDS: "postgresql://usuario:password@rds-endpoint:5432/nombre_db"
# Ejemplo para MySQL en RDS: "mysql+pymysql://usuario:password@rds-endpoint:3306/nombre_db"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Para SQLite necesitamos check_same_thread=False. Para Postgres/MySQL no es necesario,
# pero lo dejamos para que funcione out-of-the-box localmente.
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
