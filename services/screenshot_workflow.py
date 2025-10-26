"""Screenshot Workflow Orchestrator for coordinating all services."""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from config.screenshot_config import ScreenshotConfig, load_config
from services.screenshot_service import ScreenshotService, create_screenshot_service
from services.pdf_storage_service import ScreenshotStorageService, create_screenshot_storage_service
from services.data_enrichment_service import DataEnrichmentService, create_data_enrichment_service


logger = logging.getLogger(__name__)


class ScreenshotWorkflow:
    """Orchestrator for the complete screenshot-to-PDF-to-enrichment workflow."""
    
    def __init__(self, config: Optional[ScreenshotConfig] = None):
        """
        Initialize the Screenshot Workflow.
        
        Args:
            config: Optional configuration (loads from environment if not provided)
        """
        self.config = config if config else load_config()
        
        # Initialize services
        self.screenshot_service: Optional[ScreenshotService] = None
        self.storage_service: Optional[ScreenshotStorageService] = None
        self.data_enrichment_service: Optional[DataEnrichmentService] = None
        
        # Track workflow state
        self.temp_files: list[str] = []
        self._is_initialized = False
    
    def is_enabled(self) -> bool:
        """Check if screenshot functionality is enabled."""
        return self.config.enabled
    
    async def initialize(self) -> bool:
        """
        Initialize all services.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if self._is_initialized:
            logger.info("Workflow already initialized")
            return True
        
        if not self.config.enabled:
            logger.info("Screenshot functionality is disabled")
            return False
        
        try:
            logger.info("Initializing screenshot workflow...")
            
            # Initialize screenshot service
            self.screenshot_service = create_screenshot_service(self.config.playwright)
            if not await self.screenshot_service.initialize_browser():
                logger.error("Failed to initialize screenshot service")
                return False
            
            # Initialize screenshot storage service
            self.storage_service = create_screenshot_storage_service(
                self.config.imagekit
            )
            
            if not self.storage_service.is_configured():
                logger.warning("Screenshot storage service not configured - uploads will be disabled")
            
            # Initialize data enrichment service
            self.data_enrichment_service = create_data_enrichment_service()
            
            self._is_initialized = True
            logger.info("Screenshot workflow initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing workflow: {e}")
            await self.cleanup()
            return False
    
    async def process_url(
        self,
        url: str,
        subject: str,
        year: str,
        json_path: Optional[str] = None,
        csv_path: Optional[str] = None,
        temp_dir: str = "temp_screenshots"
    ) -> Optional[str]:
        """
        Process a URL through the complete workflow.
        
        Args:
            url: URL to capture
            subject: Subject name
            year: Year
            json_path: Optional path to JSON file to enrich
            csv_path: Optional path to CSV file to enrich
            temp_dir: Directory for temporary files
            
        Returns:
            PDF URL if successful, None otherwise
        """
        if not self._is_initialized:
            logger.error("Workflow not initialized. Call initialize() first.")
            return None
        
        screenshot_path = None
        screenshot_url = None
        
        try:
            # Create temp directory
            temp_path = Path(temp_dir)
            temp_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now()
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"{subject}_{year}_{timestamp_str}.png"
            
            screenshot_path = str(temp_path / screenshot_filename)
            
            # Track temp files for cleanup
            self.temp_files.append(screenshot_path)
            
            # Step 1: Capture screenshot
            logger.info(f"Step 1/3: Capturing screenshot of {url}")
            success = await self.screenshot_service.capture_screenshot_with_retry(
                url=url,
                output_path=screenshot_path,
                full_page=True,
                max_retries=3
            )
            
            if not success:
                logger.error("Failed to capture screenshot")
                return None
            
            # Step 2: Upload to ImageKit
            logger.info("Step 2/3: Uploading screenshot to ImageKit")
            metadata = {
                'subject': subject,
                'year': year,
                'url': url,
                'timestamp': timestamp
            }
            
            upload_result = self.storage_service.retry_upload(
                screenshot_path=screenshot_path,
                metadata=metadata,
                max_retries=3
            )
            
            if not upload_result.success:
                logger.error(f"Failed to upload screenshot: {upload_result.error_message}")
                return None
            
            screenshot_url = upload_result.url
            logger.info(f"Screenshot uploaded successfully: {screenshot_url}")
            
            # Step 3: Enrich data files
            if json_path or csv_path:
                logger.info("Step 3/3: Enriching data files")
                if not self.data_enrichment_service.enrich_files(
                    json_path=json_path,
                    csv_path=csv_path,
                    pdf_url=screenshot_url,  # Using screenshot URL instead of PDF
                    create_backup=True
                ):
                    logger.error("Failed to enrich data files")
                    # Don't return None - we still have the screenshot URL
            
            logger.info("Workflow completed successfully")
            return screenshot_url
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            return None
        
        finally:
            # Cleanup temporary files
            self._cleanup_temp_files()
    
    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files created during workflow."""
        if self.storage_service:
            self.storage_service.cleanup_temp_files(*self.temp_files)
        self.temp_files.clear()
    
    async def cleanup(self) -> None:
        """Clean up all resources."""
        logger.info("Cleaning up workflow resources...")
        
        # Cleanup temp files
        self._cleanup_temp_files()
        
        # Cleanup screenshot service
        if self.screenshot_service:
            await self.screenshot_service.cleanup_browser()
        
        self._is_initialized = False
        logger.info("Workflow cleanup complete")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


class ScreenshotWorkflowManager:
    """Manager for running screenshot workflows with progress tracking."""
    
    def __init__(self, config: Optional[ScreenshotConfig] = None):
        """
        Initialize the workflow manager.
        
        Args:
            config: Optional configuration
        """
        self.config = config if config else load_config()
        self.workflow: Optional[ScreenshotWorkflow] = None
    
    async def process_single(
        self,
        url: str,
        subject: str,
        year: str,
        json_path: Optional[str] = None,
        csv_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Process a single URL through the workflow.
        
        Args:
            url: URL to capture
            subject: Subject name
            year: Year
            json_path: Optional path to JSON file to enrich
            csv_path: Optional path to CSV file to enrich
            
        Returns:
            PDF URL if successful, None otherwise
        """
        async with ScreenshotWorkflow(self.config) as workflow:
            return await workflow.process_url(
                url=url,
                subject=subject,
                year=year,
                json_path=json_path,
                csv_path=csv_path
            )
    
    async def process_batch(
        self,
        items: list[Dict[str, Any]]
    ) -> list[Optional[str]]:
        """
        Process multiple URLs through the workflow.
        
        Args:
            items: List of dictionaries containing url, subject, year, json_path, csv_path
            
        Returns:
            List of PDF URLs (None for failed items)
        """
        results = []
        
        async with ScreenshotWorkflow(self.config) as workflow:
            for idx, item in enumerate(items, 1):
                logger.info(f"Processing item {idx}/{len(items)}")
                
                pdf_url = await workflow.process_url(
                    url=item['url'],
                    subject=item['subject'],
                    year=item['year'],
                    json_path=item.get('json_path'),
                    csv_path=item.get('csv_path')
                )
                
                results.append(pdf_url)
        
        successful = sum(1 for r in results if r is not None)
        logger.info(f"Batch processing complete: {successful}/{len(items)} successful")
        
        return results


def create_workflow_manager(config: Optional[ScreenshotConfig] = None) -> ScreenshotWorkflowManager:
    """
    Factory function to create a ScreenshotWorkflowManager instance.
    
    Args:
        config: Optional configuration
        
    Returns:
        ScreenshotWorkflowManager instance
    """
    return ScreenshotWorkflowManager(config)