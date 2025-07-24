import os
import shutil
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import Tuple
from pathlib import Path
import uuid
from datetime import datetime

from ..config import settings
from ..models import DocumentCreate, Document
from .document_service import DocumentService

class UploadService:
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Validate uploaded file type and size"""
        # Check file size
        if hasattr(file, 'size') and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Check file type
        file_extension = Path(file.filename).suffix.lower().lstrip('.')
        if file_extension not in settings.allowed_file_types:
            raise HTTPException(
                status_code=415,
                detail=f"File type '{file_extension}' not supported. Allowed types: {', '.join(settings.allowed_file_types)}"
            )
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> Tuple[str, str, int]:
        """Save uploaded file to disk and return file info"""
        # Generate unique filename to avoid conflicts
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(settings.uploads_directory, unique_filename)
        
        # Ensure uploads directory exists
        os.makedirs(settings.uploads_directory, exist_ok=True)
        
        # Save file to disk
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                file_size = len(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        return file_path, unique_filename, file_size
    
    @staticmethod
    def extract_basic_text(file_path: str, file_type: str) -> str:
        """Basic text extraction for Phase 1 - simple implementations"""
        try:
            if file_type.lower() in ['txt', 'md']:
                # Read text files directly
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_type.lower() == 'pdf':
                # Basic PDF text extraction using PyMuPDF
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(file_path)
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    return text
                except ImportError:
                    # Fallback if PyMuPDF not installed
                    return f"PDF file uploaded: {os.path.basename(file_path)}. Text extraction requires PyMuPDF."
            
            else:
                # For other file types, return filename for now
                return f"File uploaded: {os.path.basename(file_path)}. Full text extraction will be implemented in later phases."
                
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    @staticmethod
    async def upload_file(db: Session, file: UploadFile) -> Document:
        """Complete file upload process"""
        # Validate file
        UploadService.validate_file(file)
        
        # Save file to disk
        file_path, unique_filename, file_size = await UploadService.save_uploaded_file(file)
        
        # Get file type
        file_extension = Path(file.filename).suffix.lower().lstrip('.')
        
        # Create document record
        document_data = DocumentCreate(
            filename=unique_filename,
            original_name=file.filename,
            file_path=file_path,
            content_type="file",
            file_type=file_extension,
            file_size=file_size
        )
        
        # Save to database
        document = DocumentService.create_document(db, document_data)
        
        # Extract basic text content
        try:
            extracted_text = UploadService.extract_basic_text(file_path, file_extension)
            DocumentService.update_document_text(db, document.id, extracted_text)
            DocumentService.update_document_status(db, document.id, "completed")
        except Exception as e:
            DocumentService.update_document_status(db, document.id, "failed")
            # Log error but don't fail the upload
            print(f"Text extraction failed for document {document.id}: {str(e)}")
        
        return document
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file from disk"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Failed to delete file {file_path}: {str(e)}")
        return False 