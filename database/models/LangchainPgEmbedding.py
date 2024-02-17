
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID, FLOAT
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

# 定义基类
Base = declarative_base()


class LangchainPgEmbedding(Base):
    __tablename__ = 'langchain_pg_embedding'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    collection_id = Column(UUID(as_uuid=True), ForeignKey('langchain_pg_collection.uuid'), nullable=False)
    # 假设 embedding 字段是一个浮点数数组。这里使用 ARRAY(Float) 需要根据实际数据库支持调整
    embedding = Column(Vector(1536))
    document = Column(String)
    cmetadata = Column(JSONB)
    custom_id = Column(String)
