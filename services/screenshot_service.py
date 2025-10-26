"""Screenshot Service for capturing web page screenshots using Playwright."""

import asyncio
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page, Playwright, Error as PlaywrightError

from config.screenshot_config import PlaywrightConfig


logger = logging.getLogger(__name__)


class ScreenshotService:
    """Service for managing browser automation and screenshot capture using Playwright."""
    
    def __init__(self, config: PlaywrightConfig):
        """
        Initialize the Screenshot Service.
        
        Args:
            config: Playwright configuration settings
        """
        self.config = config
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._is_initialized = False
        
    async def initialize_browser(self, headless: Optional[bool] = None) -> bool:
        """
        Initialize the Playwright browser instance.
        
        Args:
            headless: Override config headless setting if provided
            
        Returns:
            True if initialization successful, False otherwise
        """
        if self._is_initialized:
            logger.info("Browser already initialized")
            return True
            
        try:
            logger.info(f"Initializing {self.config.browser_type} browser...")
            
            self._playwright = await async_playwright().start()
            
            # Select browser type
            browser_type = getattr(self._playwright, self.config.browser_type)
            
            # Launch browser with configuration
            headless_mode = headless if headless is not None else self.config.headless
            self._browser = await browser_type.launch(headless=headless_mode)
            
            self._is_initialized = True
            logger.info(f"Browser initialized successfully (headless={headless_mode})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            await self._cleanup_resources()
            return False
    
    async def _cleanup_resources(self):
        """Clean up browser and playwright resources."""
        if self._browser:
            try:
                await self._browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            self._browser = None
            
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
            self._playwright = None
            
        self._is_initialized = False
    
    def configure_viewport(self, width: int, height: int) -> None:
        """
        Configure viewport dimensions.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        self.config.viewport_width = width
        self.config.viewport_height = height
        logger.info(f"Viewport configured to {width}x{height}")
    
    async def capture_screenshot(
        self, 
        url: str, 
        output_path: str,
        full_page: bool = False,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Capture a screenshot of the specified URL.
        
        Args:
            url: URL to capture
            output_path: Path where screenshot will be saved
            full_page: Whether to capture full page or just viewport
            timeout: Override default timeout in milliseconds
            
        Returns:
            True if screenshot captured successfully, False otherwise
        """
        if not self._is_initialized:
            logger.error("Browser not initialized. Call initialize_browser() first.")
            return False
        
        page: Optional[Page] = None
        try:
            # Create new page with viewport configuration
            page = await self._browser.new_page(
                viewport={
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                }
            )
            
            # Set timeout
            page_timeout = timeout if timeout is not None else self.config.timeout
            page.set_default_timeout(page_timeout)
            
            logger.info(f"Navigating to {url}...")
            # Use 'domcontentloaded' for initial load, then wait for network idle
            await page.goto(url, wait_until='domcontentloaded', timeout=page_timeout)
            
            # Wait for page to be fully loaded
            try:
                # Wait for network to be idle (no requests for 500ms)
                await page.wait_for_load_state('networkidle', timeout=10000)
                logger.info("Page fully loaded (network idle)")
            except Exception as e:
                logger.warning(f"Network idle timeout, continuing anyway: {e}")
            
            # Additional wait for any dynamic content
            await page.wait_for_timeout(3000)  # 3 seconds
            
            # Check if page has content
            try:
                body_content = await page.content()
                if len(body_content) < 1000:
                    logger.warning("Page content seems very small, might not have loaded properly")
                else:
                    logger.info(f"Page content loaded ({len(body_content)} characters)")
            except Exception as e:
                logger.warning(f"Could not check page content: {e}")
            
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Capture screenshot
            logger.info(f"Capturing {'full-page' if full_page else 'viewport'} screenshot...")
            await page.screenshot(
                path=output_path,
                full_page=full_page,
                type=self.config.screenshot_format
            )
            
            logger.info(f"Screenshot saved to {output_path}")
            return True
            
        except PlaywrightError as e:
            logger.error(f"Playwright error capturing screenshot from {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error capturing screenshot from {url}: {e}")
            return False
        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
    
    async def capture_full_page_screenshot(
        self, 
        url: str, 
        output_path: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Capture a full-page screenshot of the specified URL.
        
        Args:
            url: URL to capture
            output_path: Path where screenshot will be saved
            timeout: Override default timeout in milliseconds
            
        Returns:
            True if screenshot captured successfully, False otherwise
        """
        return await self.capture_screenshot(url, output_path, full_page=True, timeout=timeout)
    
    async def capture_screenshot_with_retry(
        self,
        url: str,
        output_path: str,
        full_page: bool = False,
        max_retries: int = 3,
        retry_delay: int = 2
    ) -> bool:
        """
        Capture screenshot with retry logic for failed attempts.
        
        Args:
            url: URL to capture
            output_path: Path where screenshot will be saved
            full_page: Whether to capture full page or just viewport
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if screenshot captured successfully, False otherwise
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Screenshot attempt {attempt + 1}/{max_retries} for {url}")
                
                success = await self.capture_screenshot(url, output_path, full_page)
                
                if success:
                    return True
                
                if attempt < max_retries - 1:
                    logger.warning(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
        
        logger.error(f"Failed to capture screenshot after {max_retries} attempts")
        return False
    
    async def cleanup_browser(self) -> None:
        """Clean up browser resources and close connections."""
        logger.info("Cleaning up browser resources...")
        await self._cleanup_resources()
        logger.info("Browser cleanup complete")
    
    def is_initialized(self) -> bool:
        """Check if browser is initialized and ready."""
        return self._is_initialized
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup_browser()


def create_screenshot_service(config: PlaywrightConfig) -> ScreenshotService:
    """
    Factory function to create a ScreenshotService instance.
    
    Args:
        config: Playwright configuration
        
    Returns:
        Configured ScreenshotService instance
    """
    return ScreenshotService(config)