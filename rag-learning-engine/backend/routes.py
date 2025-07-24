from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .models import get_db, DocumentResponse, UploadResponse, DocumentLibraryResponse
from .services.upload_service import UploadService
from .services.document_service import DocumentService

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document file (PDF, TXT, MD, DOC)"""
    try:
        # Upload file and process
        document = await UploadService.upload_file(db, file)
        
        return UploadResponse(
            document_id=document.id,
            filename=document.original_name,
            status="uploaded",
            processing_status=document.processing_status
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/documents", response_model=DocumentLibraryResponse)
async def get_document_library(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all uploaded documents with chunk counts"""
    try:
        # Get documents with chunk counts
        documents = DocumentService.get_documents_with_chunk_count(db)
        total_count = DocumentService.get_documents_count(db)
        
        # Convert to response format
        document_responses = []
        for doc_dict in documents:
            document_responses.append(DocumentResponse(**doc_dict))
        
        return DocumentLibraryResponse(
            documents=document_responses,
            total_count=total_count
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get specific document details"""
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get chunk count
    chunks = getattr(document, 'chunks', [])
    chunk_count = len(chunks) if chunks else 0
    
    # Convert to response
    doc_dict = {
        'id': document.id,
        'filename': document.filename,
        'original_name': document.original_name,
        'file_path': document.file_path,
        'source_url': document.source_url,
        'content_type': document.content_type,
        'file_type': document.file_type,
        'file_size': document.file_size,
        'upload_date': document.upload_date,
        'processing_status': document.processing_status,
        'chunk_count': chunk_count
    }
    
    return DocumentResponse(**doc_dict)

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document and its associated file"""
    # Get document info first
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk if it exists
    if document.file_path and document.content_type == "file":
        UploadService.delete_file(document.file_path)
    
    # Delete from database
    success = DocumentService.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
    
    return {"message": "Document deleted successfully"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "upload-api"} 