from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Document, DocumentCreate, DocumentResponse
from sqlalchemy import func

class DocumentService:
    @staticmethod
    def create_document(db: Session, document: DocumentCreate) -> Document:
        """Create a new document record in database"""
        db_document = Document(**document.dict())
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    @staticmethod
    def get_document(db: Session, document_id: int) -> Optional[Document]:
        """Get a specific document by ID"""
        return db.query(Document).filter(Document.id == document_id).first()
    
    @staticmethod
    def get_documents(db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get list of all documents with pagination"""
        return db.query(Document).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_documents_count(db: Session) -> int:
        """Get total count of documents"""
        return db.query(func.count(Document.id)).scalar()
    
    @staticmethod
    def update_document_status(db: Session, document_id: int, status: str) -> Optional[Document]:
        """Update document processing status"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.processing_status = status
            db.commit()
            db.refresh(document)
        return document
    
    @staticmethod
    def update_document_text(db: Session, document_id: int, extracted_text: str) -> Optional[Document]:
        """Update document extracted text"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.extracted_text = extracted_text
            db.commit()
            db.refresh(document)
        return document
    
    @staticmethod
    def delete_document(db: Session, document_id: int) -> bool:
        """Delete a document and its chunks"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            db.delete(document)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_documents_with_chunk_count(db: Session) -> List[dict]:
        """Get documents with their chunk counts for library display"""
        results = db.query(
            Document,
            func.count(Document.chunks).label('chunk_count')
        ).outerjoin(Document.chunks).group_by(Document.id).all()
        
        documents = []
        for doc, chunk_count in results:
            doc_dict = {
                'id': doc.id,
                'filename': doc.filename,
                'original_name': doc.original_name,
                'file_path': doc.file_path,
                'source_url': doc.source_url,
                'content_type': doc.content_type,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'upload_date': doc.upload_date,
                'processing_status': doc.processing_status,
                'chunk_count': chunk_count or 0
            }
            documents.append(doc_dict)
        
        return documents 