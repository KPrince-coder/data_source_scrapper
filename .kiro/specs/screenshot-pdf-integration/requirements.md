# Requirements Document

## Introduction

This feature enhances the existing BECE Questions Data Scraper by integrating Playwright for taking screenshots of web pages and ImageKit for storing these screenshots as PDFs. The system will capture visual representations of question pages and embed the resulting PDF URLs into the existing JSON and CSV output files, providing a complete visual archive alongside the structured data.

## Glossary

- **Screenshot_Service**: The component responsible for capturing web page screenshots using Playwright
- **PDF_Storage_Service**: The component that handles PDF conversion and storage via ImageKit
- **Data_Enrichment_Service**: The component that integrates PDF URLs into existing JSON and CSV files
- **Kuulchat_Spider**: The existing Scrapy spider that extracts BECE questions
- **ImageKit_Client**: The service client for interacting with ImageKit API
- **Playwright_Browser**: The browser automation tool for capturing screenshots
- **Output_Files**: The JSON and CSV files containing scraped question data

## Requirements

### Requirement 1

**User Story:** As a data analyst, I want screenshots of question pages stored as PDFs in ImageKit, so that I can have visual references alongside the structured data.

#### Acceptance Criteria

1. WHEN the Kuulchat_Spider completes scraping a page, THE Screenshot_Service SHALL capture a full-page screenshot of the source URL
2. WHEN a screenshot is captured, THE PDF_Storage_Service SHALL convert the screenshot to PDF format and upload it to ImageKit
3. WHEN the PDF is successfully uploaded, THE PDF_Storage_Service SHALL return the ImageKit URL for the stored PDF
4. THE Screenshot_Service SHALL handle browser initialization and cleanup automatically
5. THE PDF_Storage_Service SHALL include metadata such as subject, year, and timestamp in the PDF filename

### Requirement 2

**User Story:** As a researcher, I want PDF URLs embedded in my existing data files, so that I can easily access visual references for each question set.

#### Acceptance Criteria

1. WHEN a PDF URL is generated, THE Data_Enrichment_Service SHALL add the URL to the corresponding JSON output file
2. WHEN a PDF URL is generated, THE Data_Enrichment_Service SHALL add the URL to the corresponding CSV output file
3. THE Data_Enrichment_Service SHALL preserve all existing data structure and fields in the output files
4. THE Data_Enrichment_Service SHALL add PDF URLs under a new field called "page_screenshot_pdf"
5. IF PDF generation fails, THE Data_Enrichment_Service SHALL record an empty string or null value for the PDF URL field

### Requirement 3

**User Story:** As a system administrator, I want the screenshot and PDF generation process to be configurable and robust, so that the system can handle errors gracefully without breaking existing functionality.

#### Acceptance Criteria

1. THE Screenshot_Service SHALL provide configuration options for screenshot quality, format, and viewport size
2. THE PDF_Storage_Service SHALL implement retry logic for failed uploads with exponential backoff
3. IF screenshot capture fails, THE Screenshot_Service SHALL log the error and continue processing without stopping the scraper
4. IF PDF upload fails after retries, THE PDF_Storage_Service SHALL log the failure and return a null URL
5. THE Screenshot_Service SHALL support headless browser operation for server environments

### Requirement 4

**User Story:** As a developer, I want the new functionality to integrate seamlessly with the existing codebase, so that current workflows remain unaffected.

#### Acceptance Criteria

1. THE Screenshot_Service SHALL integrate with the existing run_spider.py workflow without modifying core scraping logic
2. THE Data_Enrichment_Service SHALL work with existing JSON and CSV generation processes
3. THE PDF_Storage_Service SHALL be optional and configurable via environment variables or configuration files
4. THE Screenshot_Service SHALL not interfere with existing image downloading functionality
5. WHERE screenshot functionality is disabled, THE system SHALL continue normal operation without PDF URL fields

### Requirement 5

**User Story:** As a content manager, I want organized PDF storage with proper naming conventions, so that I can easily locate and manage visual archives.

#### Acceptance Criteria

1. THE PDF_Storage_Service SHALL use consistent naming patterns: "{subject}_{year}_{timestamp}.pdf"
2. THE PDF_Storage_Service SHALL organize PDFs in ImageKit folders by subject and year
3. THE PDF_Storage_Service SHALL include metadata tags for subject, year, and scraping date
4. THE PDF_Storage_Service SHALL support batch operations for multiple screenshots
5. THE PDF_Storage_Service SHALL provide methods to list and manage stored PDFs
