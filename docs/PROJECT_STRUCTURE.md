# Project Structure

This document provides an overview of the BECE Questions Data Scraper project organization.

## Directory Structure

```text
data_source_scraper/
├── 📁 config/                    # Configuration management
│   ├── screenshot_config.py      # Screenshot and ImageKit configuration
│   └── logging_config.py         # Logging setup and configuration
│
├── 📁 core/                      # Core scraper functionality
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # Main Scrapy spider (KuulchatSpider)
│   ├── restructure_questions.py  # JSON/CSV data restructuring
│   ├── generate_reports.py       # Report generation utilities
│   └── image_downloader.py       # Image downloading and processing
│
├── 📁 services/                  # Screenshot integration services
│   ├── __init__.py               # Package initialization
│   ├── screenshot_service.py     # Playwright browser automation
│   ├── screenshot_storage_service.py # ImageKit upload and management
│   ├── data_enrichment_service.py # JSON/CSV file enhancement
│   └── screenshot_workflow.py    # Complete workflow orchestration
│
├── 📁 tests/                     # Test files
│   ├── test_screenshot.py        # Screenshot capture tests
│   └── test_upload.py           # ImageKit upload tests
│
├── 📁 docs/                      # Documentation
│   ├── SCREENSHOT_INTEGRATION.md # Complete setup guide
│   ├── API_REFERENCE.md          # Detailed API documentation
│   ├── CONTRIBUTING.md           # Development guidelines
│   ├── TESTING.md               # Testing procedures
│   ├── QUICK_START_SCREENSHOTS.md # 5-minute setup guide
│   ├── CHANGELOG.md             # Version history
│   └── PROJECT_STRUCTURE.md     # This file
│
├── 📁 data/                      # Output data (generated)
│   └── subject_year/             # Individual subject-year directories
│       ├── subject_year.json     # Main data file
│       ├── subject_year.csv      # CSV format
│       ├── subject_year_metadata.json # Processing metadata
│       ├── images/               # Downloaded images
│       └── reports/              # Processing reports
│
├── 📁 logs/                      # Application logs (generated)
│   └── screenshot_workflow_*.log # Timestamped log files
│
├── 📁 temp_screenshots/          # Temporary screenshot files (generated)
│
├── 📄 run_spider.py              # Main CLI interface
├── 📄 pyproject.toml             # Project dependencies and metadata
├── 📄 README.md                  # Main project documentation
├── 📄 .env.example               # Environment variable template
├── 📄 .env                       # Environment variables (user-created)
└── 📄 .gitignore                 # Git ignore rules
```

## Module Responsibilities

### 🔧 Core Modules (`core/`)

#### `main.py` - KuulchatSpider

- **Purpose**: Main Scrapy spider for extracting BECE questions
- **Key Features**:
  - Parses objective and theory questions
  - Handles complex question structures with subparts
  - Extracts images and diagrams
  - Cleans and normalizes text content

#### `restructure_questions.py`

- **Purpose**: Transforms raw scraped data into structured formats
- **Key Features**:
  - Converts spider output to organized JSON
  - Generates CSV files with flattened data
  - Creates metadata files
  - Integrates with image downloader

#### `image_downloader.py`

- **Purpose**: Downloads and organizes question images
- **Key Features**:
  - Downloads images from scraped URLs
  - Organizes by question type (objectives/theory)
  - Generates download reports
  - Handles duplicate and invalid images

#### `generate_reports.py`

- **Purpose**: Creates processing and download reports
- **Key Features**:
  - Summarizes scraping statistics
  - Reports on image download success/failures
  - Generates processing summaries

### 🖼️ Screenshot Services (`services/`)

#### `screenshot_service.py` - ScreenshotService

- **Purpose**: Browser automation for screenshot capture
- **Key Features**:
  - Playwright browser management
  - Full-page screenshot capture
  - Retry logic and error handling
  - Multiple browser support

#### `screenshot_storage_service.py` - ScreenshotStorageService

- **Purpose**: ImageKit integration for cloud storage
- **Key Features**:
  - PNG upload to ImageKit
  - Organized folder structure
  - Cache-busting URL generation
  - Batch upload capabilities

#### `data_enrichment_service.py` - DataEnrichmentService

- **Purpose**: Enhances JSON/CSV files with screenshot URLs
- **Key Features**:
  - Adds screenshot URLs to existing files
  - Backup and rollback functionality
  - File integrity validation
  - Preserves existing data structure

#### `screenshot_workflow.py` - ScreenshotWorkflow

- **Purpose**: Orchestrates the complete screenshot workflow
- **Key Features**:
  - Coordinates all screenshot services
  - Progress tracking and reporting
  - Resource cleanup and management
  - Error recovery and logging

### ⚙️ Configuration (`config/`)

#### `screenshot_config.py`

- **Purpose**: Centralized configuration management
- **Key Features**:
  - Environment variable loading
  - Configuration validation
  - Default value management
  - ImageKit and Playwright settings

#### `logging_config.py`

- **Purpose**: Application logging setup
- **Key Features**:
  - Console and file logging
  - Configurable log levels
  - Timestamped log files
  - Third-party logger management

## Data Flow

### 1. Core Scraping Flow

```text
URL → KuulchatSpider → Raw Data → restructure_questions → JSON/CSV + Images
```

### 2. Screenshot Integration Flow

```text
URL → ScreenshotService → PNG → ScreenshotStorageService → ImageKit URL → DataEnrichmentService → Enhanced JSON/CSV
```

### 3. Complete Workflow

```text
run_spider.py → Core Scraping → Screenshot Integration → Final Output
```

## Import Structure

### Core Module Imports

```python
from core.main import KuulchatSpider
from core.restructure_questions import restructure_json
from core.generate_reports import generate_report_for_combination
from core.image_downloader import ImageDownloader
```

### Service Imports

```python
from services.screenshot_service import ScreenshotService
from services.screenshot_storage_service import ScreenshotStorageService
from services.data_enrichment_service import DataEnrichmentService
from services.screenshot_workflow import ScreenshotWorkflow
```

### Configuration Imports

```python
from config.screenshot_config import load_config
from config.logging_config import setup_logging
```

## File Naming Conventions

### Output Files

- **JSON**: `{subject}_{year}.json`
- **CSV**: `{subject}_{year}.csv`
- **Metadata**: `{subject}_{year}_metadata.json`
- **Screenshots**: `{subject}_{year}_{timestamp}.png`

### Log Files

- **Format**: `screenshot_workflow_{timestamp}.log`
- **Location**: `logs/` directory

### Temporary Files

- **Screenshots**: `temp_screenshots/`
- **Processing**: Cleaned up automatically

## Development Guidelines

### Adding New Core Functionality

1. Add modules to `core/` directory
2. Update imports in `run_spider.py`
3. Add tests to `tests/` directory
4. Update documentation

### Adding New Services

1. Add modules to `services/` directory
2. Follow existing service patterns
3. Include factory functions
4. Add comprehensive error handling

### Configuration Changes

1. Update `config/screenshot_config.py`
2. Update `.env.example`
3. Update validation logic
4. Update documentation

## Best Practices

### Module Organization

- **Single Responsibility**: Each module has a clear, focused purpose
- **Loose Coupling**: Modules interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together
- **Clear Dependencies**: Import structure is logical and minimal

### Error Handling

- **Graceful Degradation**: Screenshot failures don't break core scraping
- **Comprehensive Logging**: All errors are logged with context
- **Resource Cleanup**: Temporary files and browser resources are cleaned up
- **User-Friendly Messages**: Clear error messages for troubleshooting

### Testing

- **Unit Tests**: Individual module functionality
- **Integration Tests**: Service interactions
- **End-to-End Tests**: Complete workflows
- **Mock Tests**: External dependencies

This structure provides a clean separation of concerns while maintaining the flexibility to extend functionality in the future.
