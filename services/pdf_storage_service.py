"""PDF Storage Service for converting screenshots to PDFs and uploading to ImageKit."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from PIL import Image
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from config.screenshot_config import ImageKitConfig, PDFConfig


logger = logging.getLogger(__name__)


@dataclass
class PDFUploadResult:
    """Result of PDF upload operation."""
    success: bool
    url: Optional[str] = None
    file_id: Optional[str] = None
    error_message: Optional[str] = None


class PDFStorageService:
    """Service for converting screenshots to PDFs and managing ImageKit storage."""
    
    def __init__(self, imagekit_config: ImageKitConfig, pdf_config: PDFConfig):
        """
        Initialize the PDF Storage Service.
        
        Args:
            imagekit_config: ImageKit configuration settings
            pdf_config: PDF generation configuration settings
        """
        self.imagekit_config = imagekit_config
        self.pdf_config = pdf_config
        self._imagekit_client: Optional[ImageKit] = None
        
        # Initialize ImageKit client if configured
        if imagekit_config.is_configured():
            try:
                self._imagekit_client = ImageKit(
                    private_key=imagekit_config.private_key,
                    public_key=imagekit_config.public_key,
                    url_endpoint=imagekit_config.url_endpoint
                )
                logger.info("ImageKit client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ImageKit client: {e}")
                self._imagekit_client = None
        else:
            logger.warning("ImageKit not configured. PDF upload functionality will be disabled.")
    
    def is_configured(self) -> bool:
        """Check if ImageKit client is properly configured."""
        return self._imagekit_client is not None
    
    def convert_image_to_pdf(
        self, 
        image_path: str, 
        pdf_path: str,
        page_size: Optional[tuple] = None
    ) -> bool:
        """
        Convert an image to PDF format.
        
        Args:
            image_path: Path to input image file
            pdf_path: Path where PDF will be saved
            page_size: Optional page size tuple (width, height). Defaults to A4.
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            # Validate input image exists
            if not Path(image_path).exists():
                logger.error(f"Image file not found: {image_path}")
                return False
            
            # Open and validate image
            logger.info(f"Converting image to PDF: {image_path}")
            img = Image.open(image_path)
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get image dimensions
            img_width, img_height = img.size
            
            # Determine page size
            if page_size is None:
                if self.pdf_config.format.upper() == 'A4':
                    page_size = A4
                elif self.pdf_config.format.upper() == 'LETTER':
                    page_size = letter
                else:
                    page_size = A4  # Default to A4
            
            page_width, page_height = page_size
            
            # Calculate scaling to fit image on page with margins
            margin_left = self.pdf_config.margin_left
            margin_right = self.pdf_config.margin_right
            margin_top = self.pdf_config.margin_top
            margin_bottom = self.pdf_config.margin_bottom
            
            available_width = page_width - margin_left - margin_right
            available_height = page_height - margin_top - margin_bottom
            
            # Calculate scale factor to fit image
            scale_x = available_width / img_width
            scale_y = available_height / img_height
            scale = min(scale_x, scale_y)
            
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            
            # Center image on page
            x_offset = margin_left + (available_width - scaled_width) / 2
            y_offset = margin_bottom + (available_height - scaled_height) / 2
            
            # Ensure output directory exists
            Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create PDF
            c = canvas.Canvas(pdf_path, pagesize=page_size)
            
            # Save image temporarily for reportlab
            temp_img_path = str(Path(pdf_path).parent / "temp_rgb.jpg")
            img.save(temp_img_path, "JPEG", quality=self.pdf_config.quality)
            
            # Draw image on PDF
            c.drawImage(
                temp_img_path,
                x_offset,
                y_offset,
                width=scaled_width,
                height=scaled_height,
                preserveAspectRatio=True
            )
            
            c.save()
            
            # Clean up temporary image
            try:
                os.remove(temp_img_path)
            except Exception as e:
                logger.warning(f"Could not remove temporary image: {e}")
            
            logger.info(f"PDF created successfully: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting image to PDF: {e}")
            return False
    
    def generate_filename(self, subject: str, year: str, timestamp: Optional[datetime] = None) -> str:
        """
        Generate a consistent filename for PDF storage.
        
        Args:
            subject: Subject name
            year: Year
            timestamp: Optional timestamp (defaults to current time)
            
        Returns:
            Generated filename in format: {subject}_{year}_{timestamp}.pdf
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{subject}_{year}_{timestamp_str}.pdf"
        
        return filename
    
    def organize_in_folders(self, subject: str, year: str) -> str:
        """
        Generate folder path for organizing PDFs in ImageKit.
        
        Args:
            subject: Subject name
            year: Year
            
        Returns:
            Folder path in format: /screenshots/{subject}/{year}/
        """
        folder_path = self.imagekit_config.folder_structure.format(
            subject=subject,
            year=year
        )
        return folder_path
    
    def upload_pdf_to_imagekit(
        self,
        pdf_path: str,
        metadata: Dict[str, Any]
    ) -> PDFUploadResult:
        """
        Upload PDF to ImageKit with metadata.
        
        Args:
            pdf_path: Path to PDF file
            metadata: Dictionary containing subject, year, and other metadata
            
        Returns:
            PDFUploadResult with upload status and URL
        """
        if not self.is_configured():
            logger.error("ImageKit client not configured")
            return PDFUploadResult(
                success=False,
                error_message="ImageKit client not configured"
            )
        
        try:
            # Validate PDF file exists
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return PDFUploadResult(
                    success=False,
                    error_message=f"PDF file not found: {pdf_path}"
                )
            
            # Extract metadata
            subject = metadata.get('subject', 'unknown')
            year = metadata.get('year', 'unknown')
            url = metadata.get('url', '')
            
            # Generate filename and folder path
            filename = self.generate_filename(subject, year)
            folder_path = self.organize_in_folders(subject, year)
            
            logger.info(f"Uploading PDF to ImageKit: {filename}")
            logger.info(f"Destination folder: {folder_path}")
            
            # Read PDF file
            with open(pdf_path, 'rb') as file:
                file_content = file.read()
            
            # Prepare upload options
            options = UploadFileRequestOptions(
                folder=folder_path,
                tags=['screenshot', 'bece', subject, str(year)],
                custom_metadata={
                    'subject': subject,
                    'year': str(year),
                    'source_url': url,
                    'upload_date': datetime.now().isoformat()
                }
            )
            
            # Upload to ImageKit
            result = self._imagekit_client.upload_file(
                file=file_content,
                file_name=filename,
                options=options
            )
            
            if result and hasattr(result, 'url'):
                logger.info(f"PDF uploaded successfully: {result.url}")
                return PDFUploadResult(
                    success=True,
                    url=result.url,
                    file_id=getattr(result, 'file_id', None)
                )
            else:
                logger.error("Upload failed: No URL returned")
                return PDFUploadResult(
                    success=False,
                    error_message="Upload failed: No URL returned"
                )
                
        except Exception as e:
            logger.error(f"Error uploading PDF to ImageKit: {e}")
            return PDFUploadResult(
                success=False,
                error_message=str(e)
            )
    
    def retry_upload(
        self,
        pdf_path: str,
        metadata: Dict[str, Any],
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> PDFUploadResult:
        """
        Upload PDF with exponential backoff retry logic.
        
        Args:
            pdf_path: Path to PDF file
            metadata: Dictionary containing subject, year, and other metadata
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            
        Returns:
            PDFUploadResult with upload status and URL
        """
        import time
        
        last_error = None
        delay = initial_delay
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Upload attempt {attempt + 1}/{max_retries}")
                
                result = self.upload_pdf_to_imagekit(pdf_path, metadata)
                
                if result.success:
                    logger.info(f"Upload successful on attempt {attempt + 1}")
                    return result
                
                last_error = result.error_message
                
                if attempt < max_retries - 1:
                    logger.warning(f"Upload failed: {last_error}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Error on upload attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
        
        logger.error(f"Upload failed after {max_retries} attempts")
        return PDFUploadResult(
            success=False,
            error_message=f"Upload failed after {max_retries} attempts. Last error: {last_error}"
        )
    
    def batch_upload_pdfs(
        self,
        pdf_metadata_list: list[tuple[str, Dict[str, Any]]],
        use_retry: bool = True
    ) -> list[PDFUploadResult]:
        """
        Upload multiple PDFs in batch.
        
        Args:
            pdf_metadata_list: List of tuples containing (pdf_path, metadata)
            use_retry: Whether to use retry logic for uploads
            
        Returns:
            List of PDFUploadResult for each upload
        """
        results = []
        total = len(pdf_metadata_list)
        
        logger.info(f"Starting batch upload of {total} PDFs")
        
        for idx, (pdf_path, metadata) in enumerate(pdf_metadata_list, 1):
            logger.info(f"Processing PDF {idx}/{total}: {pdf_path}")
            
            if use_retry:
                result = self.retry_upload(pdf_path, metadata)
            else:
                result = self.upload_pdf_to_imagekit(pdf_path, metadata)
            
            results.append(result)
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"Batch upload complete: {successful}/{total} successful")
        
        return results
    
    def list_stored_pdfs(self, subject: Optional[str] = None, year: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        List PDFs stored in ImageKit.
        
        Args:
            subject: Optional subject filter
            year: Optional year filter
            
        Returns:
            List of file information dictionaries
        """
        if not self.is_configured():
            logger.error("ImageKit client not configured")
            return []
        
        try:
            # Build search query
            tags = ['screenshot', 'bece']
            if subject:
                tags.append(subject)
            if year:
                tags.append(str(year))
            
            # Construct folder path
            if subject and year:
                folder_path = self.organize_in_folders(subject, year)
            elif subject:
                folder_path = f"/screenshots/{subject}/"
            else:
                folder_path = "/screenshots/"
            
            logger.info(f"Listing PDFs in folder: {folder_path}")
            
            # List files from ImageKit
            result = self._imagekit_client.list_files(
                options={
                    'path': folder_path,
                    'fileType': 'non-image'  # PDFs are non-image files
                }
            )
            
            if result and hasattr(result, 'list'):
                files = result.list
                logger.info(f"Found {len(files)} PDFs")
                return [
                    {
                        'file_id': f.file_id,
                        'name': f.name,
                        'url': f.url,
                        'size': f.size,
                        'created_at': f.created_at
                    }
                    for f in files
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error listing PDFs: {e}")
            return []
    
    def delete_pdf(self, file_id: str) -> bool:
        """
        Delete a PDF from ImageKit.
        
        Args:
            file_id: ImageKit file ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.is_configured():
            logger.error("ImageKit client not configured")
            return False
        
        try:
            logger.info(f"Deleting PDF with file_id: {file_id}")
            self._imagekit_client.delete_file(file_id)
            logger.info("PDF deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting PDF: {e}")
            return False
    
    def cleanup_temp_files(self, *file_paths: str) -> None:
        """
        Clean up temporary files.
        
        Args:
            *file_paths: Variable number of file paths to delete
        """
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not delete temporary file {file_path}: {e}")


def create_pdf_storage_service(
    imagekit_config: ImageKitConfig,
    pdf_config: PDFConfig
) -> PDFStorageService:
    """
    Factory function to create a PDFStorageService instance.
    
    Args:
        imagekit_config: ImageKit configuration
        pdf_config: PDF configuration
        
    Returns:
        Configured PDFStorageService instance
    """
    return PDFStorageService(imagekit_config, pdf_config)