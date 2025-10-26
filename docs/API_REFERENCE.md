# API Reference

This document provides detailed API reference for the screenshot integration services.

## Services Overview

- [ScreenshotService](#screenshotservice) - Browser automation and screenshot capture
- [ScreenshotStorageService](#screenshotstorageservice) - ImageKit upload and management
- [DataEnrichmentService](#dataenrichmentservice) - JSON/CSV file enhancement
- [ScreenshotWorkflow](#screenshotworkflow) - Workflow orchestration

---

## ScreenshotService

Manages Playwright browser automation for capturing screenshots.

### Class: `ScreenshotService`

#### Constructor

```python
ScreenshotService(config: PlaywrightConfig)
```

**Parameters:**

- `config` (PlaywrightConfig): Browser configuration settings

#### Methods

##### `initialize_browser(headless: Optional[bool] = None) -> bool`

Initialize the Playwright browser instance.

**Parameters:**

- `headless` (bool, optional): Override config headless setting

**Returns:**

- `bool`: True if initialization successful

**Example:**

```python
service = ScreenshotService(config)
success = await service.initialize_browser()
```

##### `capture_screenshot(url: str, output_path: str, full_page: bool = False, timeout: Optional[int] = None) -> bool`

Capture a screenshot of the specified URL.

**Parameters:**

- `url` (str): URL to capture
- `output_path` (str): Path where screenshot will be saved
- `full_page` (bool): Whether to capture full page or just viewport
- `timeout` (int, optional): Override default timeout in milliseconds

**Returns:**

- `bool`: True if screenshot captured successfully

**Example:**

```python
success = await service.capture_screenshot(
    url="https://example.com",
    output_path="screenshot.png",
    full_page=True
)
```

##### `capture_full_page_screenshot(url: str, output_path: str, timeout: Optional[int] = None) -> bool`

Capture a full-page screenshot (convenience method).

**Parameters:**

- `url` (str): URL to capture
- `output_path` (str): Path where screenshot will be saved
- `timeout` (int, optional): Override default timeout

**Returns:**

- `bool`: True if screenshot captured successfully

##### `capture_screenshot_with_retry(url: str, output_path: str, full_page: bool = False, max_retries: int = 3, retry_delay: int = 2) -> bool`

Capture screenshot with retry logic for failed attempts.

**Parameters:**

- `url` (str): URL to capture
- `output_path` (str): Path where screenshot will be saved
- `full_page` (bool): Whether to capture full page
- `max_retries` (int): Maximum number of retry attempts
- `retry_delay` (int): Delay between retries in seconds

**Returns:**

- `bool`: True if screenshot captured successfully

##### `cleanup_browser() -> None`

Clean up browser resources and close connections.

**Example:**

```python
await service.cleanup_browser()
```

---

## ScreenshotStorageService

Manages ImageKit upload and storage operations.

### Class: `ScreenshotStorageService`

#### Constructor

```python
ScreenshotStorageService(imagekit_config: ImageKitConfig)
```

**Parameters:**

- `imagekit_config` (ImageKitConfig): ImageKit configuration settings

#### Methods

##### `is_configured() -> bool`

Check if ImageKit client is properly configured.

**Returns:**

- `bool`: True if configured and ready

##### `upload_screenshot_to_imagekit(screenshot_path: str, metadata: Dict[str, Any]) -> UploadResult`

Upload screenshot to ImageKit.

**Parameters:**

- `screenshot_path` (str): Path to screenshot file
- `metadata` (dict): Dictionary containing subject, year, and other metadata

**Returns:**

- `UploadResult`: Upload status and URL

**Example:**

```python
metadata = {
    'subject': 'science',
    'year': '2022',
    'url': 'https://example.com'
}
result = service.upload_screenshot_to_imagekit("screenshot.png", metadata)
if result.success:
    print(f"Uploaded: {result.url}")
```

##### `retry_upload(screenshot_path: str, metadata: Dict[str, Any], max_retries: int = 3, initial_delay: float = 1.0) -> UploadResult`

Upload screenshot with exponential backoff retry logic.

**Parameters:**

- `screenshot_path` (str): Path to screenshot file
- `metadata` (dict): Metadata dictionary
- `max_retries` (int): Maximum retry attempts
- `initial_delay` (float): Initial delay between retries

**Returns:**

- `UploadResult`: Upload status and URL

##### `batch_upload_screenshots(screenshot_metadata_list: list[tuple[str, Dict[str, Any]]], use_retry: bool = True) -> list[UploadResult]`

Upload multiple screenshots in batch.

**Parameters:**

- `screenshot_metadata_list` (list): List of (screenshot_path, metadata) tuples
- `use_retry` (bool): Whether to use retry logic

**Returns:**

- `list[UploadResult]`: Results for each upload

##### `list_stored_screenshots(subject: Optional[str] = None, year: Optional[str] = None) -> list[Dict[str, Any]]`

List screenshots stored in ImageKit.

**Parameters:**

- `subject` (str, optional): Subject filter
- `year` (str, optional): Year filter

**Returns:**

- `list[dict]`: List of file information dictionaries

##### `delete_screenshot(file_id: str) -> bool`

Delete a screenshot from ImageKit.

**Parameters:**

- `file_id` (str): ImageKit file ID

**Returns:**

- `bool`: True if deletion successful

---

## DataEnrichmentService

Enhances JSON and CSV files with screenshot URLs.

### Class: `DataEnrichmentService`

#### Methods

##### `enrich_json_file(json_path: str, pdf_url: Optional[str], field_name: str = "page_screenshot") -> bool`

Add screenshot URL to JSON file at root level.

**Parameters:**

- `json_path` (str): Path to JSON file
- `pdf_url` (str, optional): Screenshot URL to add
- `field_name` (str): Name of the field to add

**Returns:**

- `bool`: True if enrichment successful

##### `enrich_csv_file(csv_path: str, pdf_url: Optional[str], field_name: str = "page_screenshot") -> bool`

Add screenshot URL column to CSV file.

**Parameters:**

- `csv_path` (str): Path to CSV file
- `pdf_url` (str, optional): Screenshot URL to add
- `field_name` (str): Name of the column to add

**Returns:**

- `bool`: True if enrichment successful

##### `enrich_files(json_path: Optional[str], csv_path: Optional[str], pdf_url: Optional[str], create_backup: bool = True) -> bool`

Enrich both JSON and CSV files with screenshot URL.

**Parameters:**

- `json_path` (str, optional): Path to JSON file
- `csv_path` (str, optional): Path to CSV file
- `pdf_url` (str, optional): Screenshot URL to add
- `create_backup` (bool): Whether to create backup before modification

**Returns:**

- `bool`: True if all enrichments successful

**Example:**

```python
service = DataEnrichmentService()
success = service.enrich_files(
    json_path="data.json",
    csv_path="data.csv",
    pdf_url="https://ik.imagekit.io/example.png",
    create_backup=True
)
```

---

## ScreenshotWorkflow

Orchestrates the complete screenshot workflow.

### Class: `ScreenshotWorkflow`

#### Constructor

```python
ScreenshotWorkflow(config: Optional[ScreenshotConfig] = None)
```

**Parameters:**

- `config` (ScreenshotConfig, optional): Configuration (loads from environment if not provided)

#### Methods

##### `initialize() -> bool`

Initialize all services.

**Returns:**

- `bool`: True if initialization successful

##### `process_url(url: str, subject: str, year: str, json_path: Optional[str] = None, csv_path: Optional[str] = None, temp_dir: str = "temp_screenshots") -> Optional[str]`

Process a URL through the complete workflow.

**Parameters:**

- `url` (str): URL to capture
- `subject` (str): Subject name
- `year` (str): Year
- `json_path` (str, optional): Path to JSON file to enrich
- `csv_path` (str, optional): Path to CSV file to enrich
- `temp_dir` (str): Directory for temporary files

**Returns:**

- `str | None`: Screenshot URL if successful, None otherwise

**Example:**

```python
async with ScreenshotWorkflow() as workflow:
    screenshot_url = await workflow.process_url(
        url="https://example.com",
        subject="science",
        year="2022",
        json_path="output.json",
        csv_path="output.csv"
    )
    if screenshot_url:
        print(f"Screenshot available: {screenshot_url}")
```

##### `cleanup() -> None`

Clean up all resources.

---

## Data Models

### UploadResult

Result of screenshot upload operation.

```python
@dataclass
class UploadResult:
    success: bool
    url: Optional[str] = None
    file_id: Optional[str] = None
    error_message: Optional[str] = None
```

**Fields:**

- `success` (bool): Whether upload was successful
- `url` (str, optional): URL of uploaded screenshot
- `file_id` (str, optional): ImageKit file ID
- `error_message` (str, optional): Error message if upload failed

### Configuration Classes

#### PlaywrightConfig

```python
@dataclass
class PlaywrightConfig:
    browser_type: str = "chromium"
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 60000
    screenshot_format: str = "png"
    quality: int = 90
```

#### ImageKitConfig

```python
@dataclass
class ImageKitConfig:
    public_key: Optional[str] = None
    private_key: Optional[str] = None
    url_endpoint: Optional[str] = None
    folder_structure: str = "/screenshots/{subject}/{year}/"
```

#### ScreenshotConfig

```python
@dataclass
class ScreenshotConfig:
    enabled: bool = True
    playwright: PlaywrightConfig = None
    imagekit: ImageKitConfig = None
```

---

## Factory Functions

### `create_screenshot_service(config: PlaywrightConfig) -> ScreenshotService`

Create a configured ScreenshotService instance.

### `create_screenshot_storage_service(imagekit_config: ImageKitConfig) -> ScreenshotStorageService`

Create a configured ScreenshotStorageService instance.

### `create_data_enrichment_service() -> DataEnrichmentService`

Create a DataEnrichmentService instance.

### `create_workflow_manager(config: Optional[ScreenshotConfig] = None) -> ScreenshotWorkflowManager`

Create a ScreenshotWorkflowManager instance.

---

## Error Handling

All services implement comprehensive error handling:

- **Graceful degradation**: Screenshot failures don't break data extraction
- **Retry logic**: Automatic retries with exponential backoff
- **Detailed logging**: Comprehensive error messages and context
- **Resource cleanup**: Automatic cleanup of temporary files and browser resources

## Examples

### Basic Usage

```python
from config.screenshot_config import load_config
from services.screenshot_workflow import ScreenshotWorkflow

# Load configuration
config = load_config()

# Process single URL
async with ScreenshotWorkflow(config) as workflow:
    url = await workflow.process_url(
        url="https://example.com",
        subject="science",
        year="2022"
    )
```

### Manual Service Usage

```python
from services.screenshot_service import create_screenshot_service
from services.screenshot_storage_service import create_screenshot_storage_service

# Initialize services
screenshot_service = create_screenshot_service(config.playwright)
storage_service = create_screenshot_storage_service(config.imagekit)

# Capture and upload
await screenshot_service.initialize_browser()
success = await screenshot_service.capture_full_page_screenshot(
    "https://example.com", 
    "screenshot.png"
)

if success:
    result = storage_service.upload_screenshot_to_imagekit(
        "screenshot.png",
        {"subject": "science", "year": "2022"}
    )
    print(f"Uploaded: {result.url}")

await screenshot_service.cleanup_browser()
```
