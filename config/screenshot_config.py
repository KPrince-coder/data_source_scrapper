"""Configuration management for screenshot and PDF functionality."""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file if present


@dataclass
class ScrapyPlaywrightConfig:
    """Configuration for scrapy-playwright integration."""
    browser_type: str = "chromium"
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 30000
    screenshot_format: str = "png"
    quality: int = 90
    # scrapy-playwright specific settings
    screenshot_enabled: bool = True
    screenshot_full_page: bool = True


@dataclass
class ImageKitConfig:
    """Configuration for ImageKit integration."""
    public_key: Optional[str] = None
    private_key: Optional[str] = None
    url_endpoint: Optional[str] = None
    folder_structure: str = "/screenshots/{subject}/{year}/"
    
    def __post_init__(self):
        """Load ImageKit credentials from environment variables."""
        self.public_key = os.getenv('IMAGEKIT_PUBLIC_KEY')
        self.private_key = os.getenv('IMAGEKIT_PRIVATE_KEY')
        self.url_endpoint = os.getenv('IMAGEKIT_URL_ENDPOINT')
    
    def is_configured(self) -> bool:
        """Check if all required ImageKit credentials are available."""
        return all([self.public_key, self.private_key, self.url_endpoint])


@dataclass
class PDFConfig:
    """Configuration for PDF generation settings."""
    quality: int = 95
    format: str = "A4"
    margin_top: int = 20
    margin_bottom: int = 20
    margin_left: int = 20
    margin_right: int = 20


@dataclass
class ScreenshotConfig:
    """Main configuration class for screenshot functionality."""
    enabled: bool = True
    scrapy_playwright: ScrapyPlaywrightConfig = None
    imagekit: ImageKitConfig = None
    pdf: PDFConfig = None
    
    def __post_init__(self):
        """Initialize sub-configurations if not provided."""
        if self.scrapy_playwright is None:
            self.scrapy_playwright = ScrapyPlaywrightConfig()
        if self.imagekit is None:
            self.imagekit = ImageKitConfig()
        if self.pdf is None:
            self.pdf = PDFConfig()
    
    @classmethod
    def from_env(cls) -> 'ScreenshotConfig':
        """Create configuration from environment variables."""
        enabled = os.getenv('SCREENSHOT_ENABLED', 'true').lower() == 'true'
        
        # Scrapy-Playwright configuration from environment
        scrapy_playwright_config = ScrapyPlaywrightConfig(
            browser_type=os.getenv('PLAYWRIGHT_BROWSER', 'chromium'),
            headless=os.getenv('PLAYWRIGHT_HEADLESS', 'true').lower() == 'true',
            viewport_width=int(os.getenv('PLAYWRIGHT_VIEWPORT_WIDTH', '1920')),
            viewport_height=int(os.getenv('PLAYWRIGHT_VIEWPORT_HEIGHT', '1080')),
            timeout=int(os.getenv('PLAYWRIGHT_TIMEOUT', '30000')),
            screenshot_format=os.getenv('PLAYWRIGHT_SCREENSHOT_FORMAT', 'png'),
            quality=int(os.getenv('PLAYWRIGHT_QUALITY', '90')),
            screenshot_enabled=os.getenv('PLAYWRIGHT_SCREENSHOT_ENABLED', 'true').lower() == 'true',
            screenshot_full_page=os.getenv('PLAYWRIGHT_SCREENSHOT_FULL_PAGE', 'true').lower() == 'true'
        )
        
        # PDF configuration from environment
        pdf_config = PDFConfig(
            quality=int(os.getenv('PDF_QUALITY', '95')),
            format=os.getenv('PDF_FORMAT', 'A4'),
            margin_top=int(os.getenv('PDF_MARGIN_TOP', '20')),
            margin_bottom=int(os.getenv('PDF_MARGIN_BOTTOM', '20')),
            margin_left=int(os.getenv('PDF_MARGIN_LEFT', '20')),
            margin_right=int(os.getenv('PDF_MARGIN_RIGHT', '20'))
        )
        
        return cls(
            enabled=enabled,
            scrapy_playwright=scrapy_playwright_config,
            imagekit=ImageKitConfig(),  # Will load from env in __post_init__
            pdf=pdf_config
        )
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration and return validation results."""
        errors = []
        
        if self.enabled:
            # Validate ImageKit configuration
            if not self.imagekit.is_configured():
                missing_vars = []
                if not self.imagekit.public_key:
                    missing_vars.append('IMAGEKIT_PUBLIC_KEY')
                if not self.imagekit.private_key:
                    missing_vars.append('IMAGEKIT_PRIVATE_KEY')
                if not self.imagekit.url_endpoint:
                    missing_vars.append('IMAGEKIT_URL_ENDPOINT')
                
                errors.append(f"Missing required environment variables: {', '.join(missing_vars)}")
            
            # Validate Scrapy-Playwright configuration
            if self.scrapy_playwright.browser_type not in ['chromium', 'firefox', 'webkit']:
                errors.append(f"Invalid browser type: {self.scrapy_playwright.browser_type}")
            
            if self.scrapy_playwright.viewport_width <= 0 or self.scrapy_playwright.viewport_height <= 0:
                errors.append("Viewport dimensions must be positive integers")
            
            if self.scrapy_playwright.timeout <= 0:
                errors.append("Timeout must be a positive integer")
            
            # Validate PDF configuration
            if self.pdf.quality < 1 or self.pdf.quality > 100:
                errors.append("PDF quality must be between 1 and 100")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            'enabled': self.enabled,
            'scrapy_playwright': {
                'browser_type': self.scrapy_playwright.browser_type,
                'headless': self.scrapy_playwright.headless,
                'viewport': {
                    'width': self.scrapy_playwright.viewport_width,
                    'height': self.scrapy_playwright.viewport_height
                },
                'timeout': self.scrapy_playwright.timeout,
                'screenshot_format': self.scrapy_playwright.screenshot_format,
                'quality': self.scrapy_playwright.quality,
                'screenshot_enabled': self.scrapy_playwright.screenshot_enabled,
                'screenshot_full_page': self.scrapy_playwright.screenshot_full_page
            },
            'imagekit': {
                'public_key': self.imagekit.public_key,
                'private_key': '***' if self.imagekit.private_key else None,  # Hide private key
                'url_endpoint': self.imagekit.url_endpoint,
                'folder_structure': self.imagekit.folder_structure
            },
            'pdf': {
                'quality': self.pdf.quality,
                'format': self.pdf.format,
                'margin': {
                    'top': self.pdf.margin_top,
                    'bottom': self.pdf.margin_bottom,
                    'left': self.pdf.margin_left,
                    'right': self.pdf.margin_right
                }
            }
        }


def load_config() -> ScreenshotConfig:
    """Load configuration from environment variables with validation."""
    config = ScreenshotConfig.from_env()
    
    is_valid, errors = config.validate()
    if not is_valid and config.enabled:
        print("Warning: Screenshot configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        print("Screenshot functionality will be disabled.")
        config.enabled = False
    
    return config


# Global configuration instance
screenshot_config = load_config()