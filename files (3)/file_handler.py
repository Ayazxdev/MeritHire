"""
File Handler Service
Handles file uploads, storage, and text extraction for the pipeline
"""
import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
import PyPDF2
import io

UPLOAD_DIR = Path("/tmp/hiring_uploads")  # Change to persistent storage in production
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class FileHandler:
    """Handles file operations for candidate applications"""
    
    @staticmethod
    def get_application_dir(anon_id: str, application_id: int) -> Path:
        """Get or create directory for an application's files"""
        app_dir = UPLOAD_DIR / anon_id / str(application_id)
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
    
    @staticmethod
    async def save_file(
        file: UploadFile,
        anon_id: str,
        application_id: int,
        file_type: str  # 'resume', 'linkedin', 'certificate'
    ) -> Tuple[str, str]:
        """
        Save uploaded file and return (file_path, file_hash)
        
        Args:
            file: Uploaded file object
            anon_id: Candidate anonymous ID
            application_id: Application ID
            file_type: Type of file being saved
            
        Returns:
            Tuple of (absolute_path, sha256_hash)
        """
        app_dir = FileHandler.get_application_dir(anon_id, application_id)
        
        # Create safe filename
        original_name = file.filename or "uploaded_file.pdf"
        extension = Path(original_name).suffix
        safe_filename = f"{file_type}{extension}"
        
        file_path = app_dir / safe_filename
        
        # Read file content
        content = await file.read()
        
        # Calculate hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Save to disk
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return str(file_path), file_hash
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                
                full_text = "\n".join(text_parts)
                
                # Clean up text
                full_text = full_text.replace('\x00', '')  # Remove null bytes
                full_text = ' '.join(full_text.split())  # Normalize whitespace
                
                return full_text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    async def process_resume(
        file: UploadFile,
        anon_id: str,
        application_id: int
    ) -> Tuple[str, str, str]:
        """
        Process resume file: save and extract text
        
        Returns:
            Tuple of (file_path, file_hash, extracted_text)
        """
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("Resume must be a PDF file")
        
        # Save file
        file_path, file_hash = await FileHandler.save_file(
            file, anon_id, application_id, "resume"
        )
        
        # Extract text
        text = FileHandler.extract_text_from_pdf(file_path)
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Resume appears to be empty or unreadable. Please upload a text-based PDF.")
        
        return file_path, file_hash, text
    
    @staticmethod
    async def process_linkedin_pdf(
        file: Optional[UploadFile],
        anon_id: str,
        application_id: int
    ) -> Optional[Tuple[str, str]]:
        """
        Process LinkedIn PDF if provided
        
        Returns:
            Tuple of (file_path, extracted_text) or None if no file
        """
        if not file:
            return None
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("LinkedIn profile must be a PDF file")
        
        # Save file
        file_path, _ = await FileHandler.save_file(
            file, anon_id, application_id, "linkedin"
        )
        
        # Extract text
        text = FileHandler.extract_text_from_pdf(file_path)
        
        return file_path, text
    
    @staticmethod
    def cleanup_application_files(anon_id: str, application_id: int):
        """
        Clean up all files for an application
        (Use this for rejected/blacklisted applications)
        """
        app_dir = UPLOAD_DIR / anon_id / str(application_id)
        if app_dir.exists():
            import shutil
            shutil.rmtree(app_dir)
