# Implementation Plan

- [x] 1. Set up project dependencies and configuration




  - Add Playwright, ImageKit, and PDF processing dependencies to pyproject.toml
  - Create configuration management system for screenshot settings
  - Set up environment variable handling for ImageKit credentials
  - _Requirements: 3.1, 3.2, 4.3_



- [ ] 2. Implement Screenshot Service with Playwright integration
  - [ ] 2.1 Create ScreenshotService class with browser management
    - Implement browser initialization and cleanup methods


    - Add viewport configuration and screenshot capture functionality
    - Handle browser lifecycle management with proper async/await patterns
    - _Requirements: 1.1, 1.4, 3.5_

  - [ ] 2.2 Add screenshot capture methods with error handling
    - Implement full-page screenshot capture with timeout handling
    - Add retry logic for failed screenshot attempts
    - Create robust error handling that doesn't break existing scraper flow
    - _Requirements: 1.1, 3.3, 4.1_

  - [x]* 2.3 Write unit tests for Screenshot Service


    - Create tests for browser initialization and cleanup
    - Test screenshot capture with mock Playwright browser
    - Verify error handling scenarios and timeout behavior
    - _Requirements: 1.1, 3.3_



- [ ] 3. Implement PDF Storage Service with ImageKit integration
  - [ ] 3.1 Create PDFStorageService class with ImageKit client
    - Set up ImageKit authentication and client initialization


    - Implement PDF conversion from screenshot images using Pillow/ReportLab
    - Add filename generation with consistent naming patterns
    - _Requirements: 1.2, 1.3, 5.1, 5.2_

  - [ ] 3.2 Add upload functionality with retry logic
    - Implement PDF upload to ImageKit with metadata tagging
    - Add exponential backoff retry mechanism for failed uploads
    - Create folder organization structure in ImageKit
    - _Requirements: 1.2, 1.3, 3.2, 3.4, 5.2, 5.3_

  - [x] 3.3 Implement batch operations and management methods


    - Add batch upload capabilities for multiple PDFs
    - Create methods to list and manage stored PDFs in ImageKit
    - Implement cleanup of temporary files after processing
    - _Requirements: 5.4, 5.5_




  - [ ]* 3.4 Write unit tests for PDF Storage Service
    - Test PDF conversion functionality with sample images
    - Mock ImageKit API calls and test upload logic
    - Verify retry mechanism and error handling
    - _Requirements: 1.2, 3.2, 3.4_

- [ ] 4. Implement Data Enrichment Service for JSON/CSV integration
  - [ ] 4.1 Create DataEnrichmentService class for file modification
    - Implement JSON file enrichment while preserving existing structure
    - Add CSV file enrichment with new page_screenshot_pdf column
    - Create backup mechanism for original files before modification
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 4.2 Add file validation and integrity checking
    - Implement validation methods to ensure file integrity after modification
    - Add rollback functionality if enrichment fails
    - Handle cases where PDF generation fails with null/empty values
    - _Requirements: 2.3, 2.5, 3.4_

  - [ ]* 4.3 Write unit tests for Data Enrichment Service
    - Test JSON and CSV file modification with sample data
    - Verify backup and rollback functionality


    - Test handling of failed PDF generation scenarios
    - _Requirements: 2.1, 2.2, 2.5_

- [x] 5. Create configuration management system


  - [ ] 5.1 Implement configuration classes and validation
    - Create ScreenshotConfig class with all necessary settings
    - Add environment variable loading and validation
    - Implement configuration validation with meaningful error messages


    - _Requirements: 3.1, 3.2, 4.4_

  - [ ] 5.2 Add configuration file support and defaults
    - Create default configuration with sensible values
    - Add support for optional configuration file override
    - Implement feature toggle for enabling/disabling screenshot functionality
    - _Requirements: 4.4, 4.5_

- [ ] 6. Integrate services with existing scraper workflow
  - [ ] 6.1 Modify run_spider.py to include screenshot workflow
    - Add screenshot capture after successful page scraping




    - Integrate PDF storage and data enrichment in post-processing
    - Ensure existing functionality remains unaffected when screenshots are disabled
    - _Requirements: 4.1, 4.2, 4.5_

  - [ ] 6.2 Update restructure_questions.py for enhanced data handling
    - Modify JSON restructuring to accommodate PDF URL fields
    - Update CSV generation to include page_screenshot_pdf column
    - Ensure backward compatibility with existing data structures
    - _Requirements: 2.1, 2.2, 2.3, 4.2_


  - [ ] 6.3 Add error handling and logging integration
    - Implement comprehensive error logging for screenshot workflow
    - Add progress reporting for screenshot and PDF generation
    - Create fallback mechanisms that preserve existing scraper functionality
    - _Requirements: 3.3, 3.4, 4.1_

- [ ] 7. Create workflow orchestration and main integration
  - [ ] 7.1 Implement ScreenshotWorkflow orchestrator class
    - Create main workflow class that coordinates all services
    - Add progress tracking and status reporting
    - Implement cleanup and resource management across all services
    - _Requirements: 1.1, 1.2, 1.3, 4.1_

  - [ ] 7.2 Add command-line interface enhancements
    - Add CLI flags for enabling/disabling screenshot functionality
    - Create dry-run mode for testing screenshot workflow
    - Add verbose logging options for debugging
    - _Requirements: 3.1, 4.4, 4.5_

  - [ ]* 7.3 Write integration tests for complete workflow
    - Test end-to-end workflow from scraping to PDF storage
    - Verify integration with existing scraper functionality
    - Test error scenarios and recovery mechanisms
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2_

- [ ] 8. Add documentation and setup instructions
  - [x] 8.1 Create setup and installation documentation

    - Document ImageKit account setup and API key configuration
    - Add Playwright installation instructions and browser setup
    - Create environment variable configuration guide
    - _Requirements: 3.1, 4.4_

  - [x] 8.2 Update README with new functionality



    - Document new CLI options and configuration settings
    - Add examples of enhanced JSON/CSV output with PDF URLs
    - Include troubleshooting guide for common issues
    - _Requirements: 4.4, 4.5_