from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .config import settings

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy ORM Models
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)  # For files: original filename, For URLs: extracted title
    original_name = Column(String)  # Original filename for uploaded files
    file_path = Column(String)  # Local file path (NULL for URLs)
    source_url = Column(String)  # URL source (NULL for uploaded files)
    content_type = Column(String)  # file/url to distinguish source type
    file_type = Column(String)  # pdf, txt, md, doc, html, etc.
    file_size = Column(Integer)  # File size (NULL for URLs)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    extracted_text = Column(Text)  # Content extracted from file or URL
    
    # Relationship to chunks
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer)
    chunk_type = Column(String)  # text, table, image
    embedding_id = Column(String)  # Reference to Qdrant vector
    
    # Relationship to document
    document = relationship("Document", back_populates="chunks")

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class DocumentBase(BaseModel):
    filename: str
    original_name: Optional[str] = None
    file_path: Optional[str] = None
    source_url: Optional[str] = None
    content_type: str  # "file" or "url"
    file_type: str
    file_size: Optional[int] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    upload_date: datetime
    processing_status: str
    chunk_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class ChunkBase(BaseModel):
    chunk_text: str
    chunk_index: int
    chunk_type: str = "text"

class ChunkCreate(ChunkBase):
    document_id: int
    embedding_id: Optional[str] = None

class ChunkResponse(ChunkBase):
    id: int
    document_id: int
    embedding_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    processing_status: str

class DocumentLibraryResponse(BaseModel):
    documents: List[DocumentResponse]
    total_count: int 