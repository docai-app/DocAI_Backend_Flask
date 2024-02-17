# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
# 创建数据库引擎
engine = create_engine(os.getenv("PGVECTOR_DB_CONNECTION_STRING"))

# 创建Session类
SessionFactory = sessionmaker(bind=engine)


def get_session():
    return SessionFactory()
