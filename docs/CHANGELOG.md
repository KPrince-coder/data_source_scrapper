# Changelog

All notable changes to the BECE Questions Data Scraper project.

## [2.0.0] - 2024-10-26

### 🎉 Major Features Added

#### Screenshot Integration

- **Automatic Screenshot Capture**: Full-page screenshots using Playwright
- **Cloud Storage**: Direct PNG upload to ImageKit (no PDF conversion)
- **URL Embedding**: Screenshot URLs added to JSON and CSV output files
- **Visual Archive**: Complete visual record alongside structured data

#### New Services Architecture

- **ScreenshotService**: Browser automation and screenshot capture
- **ScreenshotStorageService**: ImageKit upload and management
- **DataEnrichmentService**: JSON/CSV file enhancement
- **ScreenshotWorkflow**: Complete workflow orchestration

#### Configuration System

- **Environment-based config**: All settings via `.env` file
- **Graceful degradation**: Works without screenshot setup
- **Comprehensive validation**: Clear error messages for misconfigurations

### 🔧 Technical Improvements

#### Dependencies

- Added `imagekitio>=4.2.0` for cloud storage
- Added `scrapy-playwright>=0.0.44` for browser automation
- Added `python-dotenv>=1.2.0` for environment management
- Removed PDF-related dependencies (reportlab, img2pdf, pillow)

#### CLI Enhancements

- `--no-screenshots`: Disable screenshot functionality
- `--verbose`: Enable debug logging
- Better error messages and progress reporting

#### File Organization

- Screenshots organized by subject and year in ImageKit
- Unique filenames with timestamps to avoid caching issues
- Automatic cleanup of temporary files

### 📚 Documentation

#### New Documentation

- **[Screenshot Integration Guide](docs/SCREENSHOT_INTEGRATION.md)**: Complete setup and usage
- **[API Reference](docs/API_REFERENCE.md)**: Detailed API documentation
- **[Contributing Guide](docs/CONTRIBUTING.md)**: Development guidelines
- **[Testing Guide](docs/TESTING.md)**: Testing procedures and debugging
- **[Quick Start](docs/QUICK_START_SCREENSHOTS.md)**: 5-minute setup guide

#### Updated Documentation

- Enhanced README with screenshot integration
- Updated installation instructions
- Added troubleshooting sections

### 🐛 Bug Fixes

#### ImageKit Upload Issues

- Fixed file upload method to use file objects instead of bytes
- Added cache-busting with `updatedAt` parameter
- Implemented proper retry logic with exponential backoff
- Fixed filename generation for unique uploads

#### Browser Automation

- Improved page loading with better wait strategies
- Enhanced error handling for timeout scenarios
- Added support for different browser types
- Better resource cleanup and memory management

### 🔄 Breaking Changes

#### Service Renaming

- `PDFStorageService` → `ScreenshotStorageService`
- Updated all imports and references
- Removed PDF conversion functionality

#### Output Format Changes

- `page_screenshot_pdf` → `page_screenshot` in JSON/CSV
- URLs now point to PNG files instead of PDFs
- Added timestamp and cache-busting parameters to URLs

#### Configuration Changes

- Removed PDF-related configuration options
- Simplified ImageKit setup requirements
- Updated environment variable names for clarity

### 🚀 Performance Improvements

#### Workflow Optimization

- Reduced processing steps (removed PDF conversion)
- Faster upload times with direct PNG upload
- Better memory usage with proper cleanup
- Parallel processing capabilities for batch operations

#### Error Recovery

- Graceful degradation when screenshots fail
- Continued data extraction even with upload failures
- Comprehensive logging for debugging
- Automatic retry mechanisms

### 📊 Output Structure

#### Enhanced JSON

```json
{
  "page_screenshot": "https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026_143052.png?updatedAt=1761494123212",
  "objectives": [...],
  "theory": [...]
}
```

#### Enhanced CSV

```csv
page_screenshot,type,number,question,...
https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026_143052.png?updatedAt=1761494123212,objectives,1,"What is...",...
```

### 🔧 Development Improvements

#### Testing

- Comprehensive test suite for all services
- Integration tests for complete workflows
- Mock tests for CI/CD environments
- Performance benchmarking

#### Code Quality

- Type hints throughout codebase
- Comprehensive error handling
- Detailed logging and debugging
- Modular service architecture

#### Development Tools

- Updated development setup instructions
- Debugging guides and troubleshooting
- Code style guidelines
- Contribution workflow

## [1.0.0] - Previous Version

### Core Features

- Web scraping of BECE questions from Kuulchat.com
- JSON and CSV output generation
- Image downloading and organization
- Batch processing capabilities
- Multi-subject and year range support

---

## Migration Guide

### From v1.0.0 to v2.0.0

#### Environment Setup

1. Install new dependencies: `uv sync`
2. Install Playwright browsers: `playwright install chromium`
3. Set up ImageKit credentials in `.env` file
4. Update any custom scripts using the old service names

#### API Changes

- Replace `PDFStorageService` with `ScreenshotStorageService`
- Update field names from `page_screenshot_pdf` to `page_screenshot`
- Remove PDF-related configuration options

#### Testing

- Run `uv run python tests/test_screenshot.py` to verify setup
- Test upload with `uv run python tests/test_upload.py`
- Verify integration with `uv run python run_spider.py -s science -y 2022`

For detailed migration instructions, see the [Screenshot Integration Guide](docs/SCREENSHOT_INTEGRATION.md).
