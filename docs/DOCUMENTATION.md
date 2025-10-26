# Code Documentation

## Overview

The BECE Questions Data Scraper consists of several Python modules working together to scrape, process, and organize educational content. Here's a detailed explanation of each component:

## Main Components

### 1. run_spider.py

The main entry point and orchestrator of the scraping process.

#### Key Functions

##### generate_url(subject: str, year: str) -> str

- Generates the full URL for a subject-year combination
- Parameters:
  - subject: The subject name (e.g., "science")
  - year: The year as string (e.g., "2022")
- Returns: Complete URL for scraping

##### validate_subject_year(subject: str, year: str) -> bool

- Validates both subject and year
- Checks:
  - Subject exists in available subjects
  - Year is within valid range (2000-present)
- Returns: True if valid, False otherwise

##### run_batch_spider(subjects: list[str], years: list[str], base_output_dir: str, dry_run: bool) -> bool

- Processes multiple subject-year combinations
- Parameters:
  - subjects: List of subjects to process
  - years: List of years to process
  - base_output_dir: Output directory path
  - dry_run: If True, only preview URLs
- Returns: True if all successful, False if any failed

##### Command Line Interface

The script supports various command-line arguments:

- `-s/--subject`: Single subject
- `-y/--year`: Single year
- `-S/--subjects`: Multiple subjects (comma-separated)
- `-Y/--years`: Year range or multiple years
- `-o/--output`: Custom output directory
- `--list`: List available subjects
- `--list-urls`: Preview URLs without scraping

### 2. main.py (KuulchatSpider)

The Scrapy spider implementation for extracting data.

#### Spider Configuration

- Custom user agent
- Respects robots.txt
- Rate limiting (2-second delay between requests)
- Single concurrent request

#### Data Extraction

- Extracts question sections
- Processes objective and theory questions
- Handles image downloads
- Structures data hierarchically

### 3. restructure_questions.py

Handles data transformation and organization.

#### Features

- JSON to structured format conversion
- Metadata generation
- CSV export
- Directory structure creation

### 4. image_downloader.py

Manages image downloads and organization.

#### Capabilities

- Parallel image downloading
- Automatic retry on failure
- Directory structure creation
- Progress tracking

### 5. generate_reports.py

Creates detailed reports about the scraping process.

#### Report Contents

- Successful downloads
- Failed downloads
- Processing statistics
- Timing information

## Data Structures

### JSON Output Format

```json
{
  "metadata": {
    "subject": "science",
    "year": "2022",
    "processed_date": "2025-09-27",
    "url": "https://kuulchat.com/bece/questions/science-2022/"
  },
  "sections": {
    "objectives": [...],
    "theory": [...]
  }
}
```

### CSV Output Format

Headers:

- section_type (objectives/theory)
- question_number
- question_text
- options (for objectives)
- correct_answer
- explanation
- image_paths

## Error Handling

The application implements comprehensive error handling:

1. Input Validation:
   - Subject validation
   - Year range validation
   - URL existence checking

2. Processing Errors:
   - Network errors
   - Parse errors
   - File system errors

3. Recovery Mechanisms:
   - Automatic retries for downloads
   - Partial success handling in batch mode
   - Cleanup on failure

## Customization

The scraper can be customized through several configuration points:

1. Subject Configuration:
   - Add/modify subjects in AVAILABLE_SUBJECTS list
   - Update BASE_URL if needed

2. Output Structure:
   - Modify base output directory
   - Change file naming patterns
   - Adjust directory structure

3. Scraping Behavior:
   - Adjust download delays
   - Configure concurrent requests
   - Modify user agent

## Best Practices

1. Rate Limiting:
   - Default 2-second delay between requests
   - Single concurrent request
   - Respect robots.txt

2. Data Organization:
   - Structured output directories
   - Clear file naming conventions
   - Separate image storage

3. Error Handling:
   - Graceful failure handling
   - Detailed error reporting
   - Clean state management
