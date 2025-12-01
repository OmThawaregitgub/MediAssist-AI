from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
from datetime import datetime
import logging

from ..database import get_db
from ..auth import get_current_user
from ..models import User, UploadedFile
from rag_pipeline import EnhancedRAGPipeline, DocumentProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt': 'text/plain',
    'csv': 'text/csv',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}

def get_rag_pipeline(user_id: int) -> EnhancedRAGPipeline:
    """Get or create RAG pipeline for user"""
    # Simplified version - in reality, you'd have a pipeline manager
    return EnhancedRAGPipeline(user_id=str(user_id))

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    process_now: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file for processing"""
    try:
        # Validate file type
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create database record
        uploaded_file = UploadedFile(
            user_id=current_user.id,
            filename=file.filename,
            filepath=file_path,
            file_type=file_extension,
            file_size=file_size,
            processed=False,
            created_at=datetime.now()
        )
        
        db.add(uploaded_file)
        db.flush()
        
        # Process file if requested
        if process_now:
            process_result = await process_uploaded_file(
                uploaded_file.id, current_user.id, db
            )
            
            return {
                "message": "File uploaded and processed successfully",
                "file_id": uploaded_file.id,
                "filename": file.filename,
                "processed": True,
                "processing_result": process_result
            }
        else:
            db.commit()
            return {
                "message": "File uploaded successfully",
                "file_id": uploaded_file.id,
                "filename": file.filename,
                "processed": False
            }
            
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.post("/process/{file_id}")
async def process_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process an uploaded file"""
    return await process_uploaded_file(file_id, current_user.id, db)

async def process_uploaded_file(file_id: int, user_id: int, db: Session):
    """Process an uploaded file and add to RAG pipeline"""
    try:
        # Get file record
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.user_id == user_id
        ).first()
        
        if not uploaded_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if uploaded_file.processed:
            return {"message": "File already processed", "document_count": 0}
        
        # Initialize document processor
        doc_processor = DocumentProcessor()
        
        # Process file
        documents = doc_processor.process_file(
            uploaded_file.filepath,
            uploaded_file.file_type
        )
        
        if not documents:
            uploaded_file.processed = True
            uploaded_file.processed_at = datetime.now()
            db.commit()
            return {"message": "No content extracted from file", "document_count": 0}
        
        # Get user's RAG pipeline and add documents
        rag = get_rag_pipeline(user_id)
        
        # Add user metadata to documents
        user_metadata = {
            'uploaded_by': user_id,
            'original_filename': uploaded_file.filename,
            'file_type': uploaded_file.file_type,
            'uploaded_at': uploaded_file.created_at.isoformat()
        }
        
        for doc in documents:
            doc['metadata'].update(user_metadata)
        
        # Add to vector store
        rag.add_documents(documents)
        
        # Update file record
        uploaded_file.processed = True
        uploaded_file.processed_at = datetime.now()
        db.commit()
        
        logger.info(f"Processed file {uploaded_file.filename}: {len(documents)} documents")
        
        return {
            "message": "File processed successfully",
            "document_count": len(documents),
            "documents": [{
                "text_preview": doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text'],
                "metadata": doc['metadata']
            } for doc in documents[:5]]  # Return first 5 documents as preview
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )

@router.get("/files")
async def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's uploaded files"""
    files = db.query(UploadedFile).filter(
        UploadedFile.user_id == current_user.id
    ).order_by(UploadedFile.created_at.desc()).all()
    
    return [
        {
            "id": file.id,
            "filename": file.filename,
            "file_type": file.file_type,
            "file_size": file.file_size,
            "processed": file.processed,
            "processed_at": file.processed_at,
            "created_at": file.created_at
        }
        for file in files
    ]

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an uploaded file"""
    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Delete physical file
        if os.path.exists(file.filepath):
            os.remove(file.filepath)
        
        # Delete database record
        db.delete(file)
        db.commit()
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )