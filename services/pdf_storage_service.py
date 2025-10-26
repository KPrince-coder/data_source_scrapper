"""Screenshot Storage Service for uploading screenshots to ImageKit."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from config.screenshot_config import ImageKitConfig


logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    """Result of screenshot upload operation."""
    success: bool
    url: Optional[str] = None
    file_id: Optional[str] = None
    error_message: Optional[str] = None


class ScreenshotStorageService:
    """Service for uploading screenshots to ImageKit storage."""
    
    def __init__(self, imagekit_config: ImageKitConfig):
        """
        Initialize the Screenshot Storage Service.
        
        Args:
            imagekit_config: ImageKit configuration settings
        """
        self.imagekit_config = imagekit_config
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
            logger.warning("ImageKit not configured. Screenshot upload functionality will be disabled.")
    
    def is_configured(self) -> bool:
        """Check if ImageKit client is properly configured."""
        return self._imagekit_client is not None
    

    
    def generate_filename(self, subject: str, year: str, timestamp: Optional[datetime] = None) -> str:
        """
        Generate a consistent filename for screenshot storage.
        
        Args:
            subject: Subject name
            year: Year
            timestamp: Optional timestamp (defaults to current time)
            
        Returns:
            Generated filename in format: {subject}_{year}.png
        """
        # Simple filename with just subject and year
        filename = f"{subject}_{year}.png"
        
        return filename
    
    def organize_in_folders(self, subject: str, year: str) -> str:
        """
        Generate folder path for organizing screenshots in ImageKit.
        
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
    
    def upload_screenshot_to_imagekit(
        self,
        screenshot_path: str,
        metadata: Dict[str, Any]
    ) -> UploadResult:
        """
        Upload screenshot to ImageKit.
        
        Args:
            screenshot_path: Path to screenshot file
            metadata: Dictionary containing subject, year, and other metadata
            
        Returns:
            UploadResult with upload status and URL
        """
        if not self.is_configured():
            logger.error("ImageKit client not configured")
            return UploadResult(
                success=False,
                error_message="ImageKit client not configured"
            )
        
        try:
            # Validate screenshot file exists
            screenshot_file = Path(screenshot_path)
            if not screenshot_file.exists():
                logger.error(f"Screenshot file not found: {screenshot_path}")
                return UploadResult(
                    success=False,
                    error_message=f"Screenshot file not found: {screenshot_path}"
                )
            
            # Extract metadata
            subject = metadata.get('subject', 'unknown')
            year = metadata.get('year', 'unknown')
            
            # Generate filename and folder path
            filename = self.generate_filename(subject, year)
            folder_path = self.organize_in_folders(subject, year)
            
            logger.info(f"Uploading screenshot to ImageKit: {filename}")
            logger.info(f"Destination folder: {folder_path}")
            
            # Log file size before upload
            file_size = screenshot_file.stat().st_size
            logger.info(f"File size: {file_size} bytes")
            
            # According to ImageKit documentation, we should pass the file object directly
            # Example from docs: file=open("sample.jpg", "rb")
            
            # Prepare upload options
            options = UploadFileRequestOptions(
                folder=folder_path,
                tags=['screenshot', 'bece', subject, str(year)],
                use_unique_file_name=False  # Use our filename as-is
            )
            
            # Upload using file object (the correct way according to docs)
            with open(screenshot_path, 'rb') as file_obj:
                result = self._imagekit_client.upload_file(
                    file=file_obj,
                    file_name=filename,
                    options=options
                )
            
            if result and hasattr(result, 'url'):
                logger.info(f"Screenshot uploaded successfully: {result.url}")
                return UploadResult(
                    success=True,
                    url=result.url,
                    file_id=getattr(result, 'file_id', None)
                )
            else:
                logger.error("Upload failed: No URL returned")
                return UploadResult(
                    success=False,
                    error_message="Upload failed: No URL returned"
                )
                
        except Exception as e:
            logger.error(f"Error uploading screenshot to ImageKit: {e}")
            return UploadResult(
                success=False,
                error_message=str(e)
            )
    
    def retry_upload(
        self,
        screenshot_path: str,
        metadata: Dict[str, Any],
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> UploadResult:
        """
        Upload screenshot with exponential backoff retry logic.
        
        Args:
            screenshot_path: Path to screenshot file
            metadata: Dictionary containing subject, year, and other metadata
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            
        Returns:
            UploadResult with upload status and URL
        """
        import time
        
        last_error = None
        delay = initial_delay
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Upload attempt {attempt + 1}/{max_retries}")
                
                result = self.upload_screenshot_to_imagekit(screenshot_path, metadata)
                
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
        return UploadResult(
            success=False,
            error_message=f"Upload failed after {max_retries} attempts. Last error: {last_error}"
        )
    
    def batch_upload_screenshots(
        self,
        screenshot_metadata_list: list[tuple[str, Dict[str, Any]]],
        use_retry: bool = True
    ) -> list[UploadResult]:
        """
        Upload multiple screenshots in batch.
        
        Args:
            screenshot_metadata_list: List of tuples containing (screenshot_path, metadata)
            use_retry: Whether to use retry logic for uploads
            
        Returns:
            List of UploadResult for each upload
        """
        results = []
        total = len(screenshot_metadata_list)
        
        logger.info(f"Starting batch upload of {total} screenshots")
        
        for idx, (screenshot_path, metadata) in enumerate(screenshot_metadata_list, 1):
            logger.info(f"Processing screenshot {idx}/{total}: {screenshot_path}")
            
            if use_retry:
                result = self.retry_upload(screenshot_path, metadata)
            else:
                result = self.upload_screenshot_to_imagekit(screenshot_path, metadata)
            
            results.append(result)
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"Batch upload complete: {successful}/{total} successful")
        
        return results
    
    def list_stored_screenshots(self, subject: Optional[str] = None, year: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        List screenshots stored in ImageKit.
        
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
            # Construct folder path
            if subject and year:
                folder_path = self.organize_in_folders(subject, year)
            elif subject:
                folder_path = f"/screenshots/{subject}/"
            else:
                folder_path = "/screenshots/"
            
            logger.info(f"Listing screenshots in folder: {folder_path}")
            
            # List files from ImageKit
            result = self._imagekit_client.list_files(
                options={
                    'path': folder_path,
                    'fileType': 'image'  # Screenshots are images
                }
            )
            
            if result and hasattr(result, 'list'):
                files = result.list
                logger.info(f"Found {len(files)} screenshots")
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
            logger.error(f"Error listing screenshots: {e}")
            return []
    
    def delete_screenshot(self, file_id: str) -> bool:
        """
        Delete a screenshot from ImageKit.
        
        Args:
            file_id: ImageKit file ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.is_configured():
            logger.error("ImageKit client not configured")
            return False
        
        try:
            logger.info(f"Deleting screenshot with file_id: {file_id}")
            self._imagekit_client.delete_file(file_id)
            logger.info("Screenshot deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting screenshot: {e}")
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


def create_screenshot_storage_service(
    imagekit_config: ImageKitConfig
) -> ScreenshotStorageService:
    """
    Factory function to create a ScreenshotStorageService instance.
    
    Args:
        imagekit_config: ImageKit configuration
        
    Returns:
        Configured ScreenshotStorageService instance
    """
    return ScreenshotStorageService(imagekit_config)