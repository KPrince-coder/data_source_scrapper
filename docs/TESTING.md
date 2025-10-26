# Testing Guide

This guide covers testing the BECE Questions Data Scraper and its screenshot functionality.

## Test Structure

```text
tests/
├── test_screenshot.py      # Screenshot capture tests
├── test_upload.py         # ImageKit upload tests
└── test_integration.py    # End-to-end workflow tests
```

## Prerequisites

### Basic Testing

For basic scraper testing (no screenshots):

```bash
uv sync
```

### Screenshot Testing

For screenshot functionality testing:

```bash
# Install Playwright browsers
playwright install chromium

# Set up ImageKit credentials in .env
IMAGEKIT_PUBLIC_KEY=your_key
IMAGEKIT_PRIVATE_KEY=your_key  
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id
```

## Running Tests

### Quick Tests

#### Test Basic Scraper

```bash
# Test scraper without screenshots
uv run python run_spider.py -s science -y 2022 --no-screenshots
```

#### Test Screenshot Capture

```bash
# Test screenshot capture (no upload)
uv run python tests/test_screenshot.py
```

#### Test ImageKit Upload

```bash
# Test upload functionality (requires credentials)
uv run python tests/test_upload.py
```

### Comprehensive Testing

#### Test Complete Workflow

```bash
# Test end-to-end with screenshots
uv run python run_spider.py -s science -y 2022 --verbose
```

#### Test Multiple Subjects

```bash
# Test batch processing
uv run python run_spider.py -S science,mathematics -Y 2022-2023
```

## Test Scenarios

### 1. Screenshot Capture Tests

**File**: `tests/test_screenshot.py`

**What it tests**:

- Browser initialization
- Page loading and navigation
- Screenshot capture
- File creation and validation
- Error handling

**Expected output**:

```text
Testing screenshot capture...
✅ Browser initialized successfully
📸 Capturing screenshot...
✅ Screenshot captured successfully!
File: test_screenshot.png
Size: 2716212 bytes
✅ Screenshot file size looks good
🧹 Browser cleanup complete
```

**Troubleshooting**:

- **Browser fails to initialize**: Run `playwright install chromium`
- **Screenshot is empty**: Check if URL is accessible
- **Timeout errors**: Increase `PLAYWRIGHT_TIMEOUT` in `.env`

### 2. ImageKit Upload Tests

**File**: `tests/test_upload.py`

**What it tests**:

- ImageKit client configuration
- File upload process
- URL generation with cache-busting
- Error handling and retries

**Expected output**:

```text
Testing ImageKit upload...
✅ Found test screenshot: test_screenshot.png
Size: 2716212 bytes
Uploading to ImageKit...
✅ Upload successful!
URL: https://ik.imagekit.io/your_id/screenshots/science/2010/science_2010_20241026_143052.png?updatedAt=1761494123212
🔗 You can view the screenshot at: [URL]
```

**Troubleshooting**:

- **"ImageKit not configured"**: Check `.env` credentials
- **Upload fails**: Verify API keys and network connection
- **File size is 16 bytes**: Old bug, should be fixed with current implementation

### 3. Integration Tests

**What it tests**:

- Complete scraper workflow
- Screenshot integration
- Data enrichment
- Error recovery

**Command**:

```bash
uv run python run_spider.py -s science -y 2022 --verbose
```

**Expected workflow**:

1. ✅ Scrapy extracts questions
2. 📸 Screenshot captured
3. ☁️ Uploaded to ImageKit  
4. 📝 URLs added to JSON/CSV
5. ✅ Process complete

## Debugging Tests

### Enable Debug Mode

```bash
# Run with verbose logging
uv run python run_spider.py -s science -y 2022 --verbose

# Run browser in visible mode (for screenshot debugging)
PLAYWRIGHT_HEADLESS=false uv run python tests/test_screenshot.py
```

### Check Log Files

```bash
# View latest logs
ls -la logs/
tail -f logs/screenshot_workflow_*.log
```

### Common Debug Commands

```bash
# Test configuration
uv run python -c "from config.screenshot_config import load_config; config = load_config(); print(f'Enabled: {config.enabled}'); print(f'ImageKit: {config.imagekit.is_configured()}')"

# Test ImageKit connection
uv run python -c "from imagekitio import ImageKit; ik = ImageKit(private_key='your_key', public_key='your_key', url_endpoint='your_endpoint'); print('Connected!')"

# Check Playwright installation
playwright --version
```

## Test Data

### Sample URLs for Testing

```python
TEST_URLS = {
    'science_2022': 'https://kuulchat.com/bece/questions/science-2022/',
    'mathematics_2021': 'https://kuulchat.com/bece/questions/mathematics-2021/',
    'english_2020': 'https://kuulchat.com/bece/questions/english-2020/'
}
```

### Expected File Sizes

- **Screenshots**: 1-5 MB (depending on page length)
- **JSON files**: 50-500 KB
- **CSV files**: 20-200 KB

## Performance Testing

### Timing Benchmarks

| Operation | Expected Time |
|-----------|---------------|
| Screenshot capture | 5-15 seconds |
| ImageKit upload | 3-8 seconds |
| Data enrichment | 1-3 seconds |
| **Total overhead** | **10-25 seconds** |

### Memory Usage

- **Browser process**: 100-300 MB
- **Python process**: 50-150 MB
- **Peak usage**: ~500 MB

### Load Testing

```bash
# Test multiple subjects (stress test)
uv run python run_spider.py -S science,mathematics,english,social-studies -Y 2020-2022
```

## Error Scenarios

### Network Issues

```bash
# Test with poor connection
# Screenshots should retry and eventually succeed or fail gracefully
```

### Invalid Credentials

```bash
# Test with wrong ImageKit keys
IMAGEKIT_PRIVATE_KEY=invalid uv run python tests/test_upload.py
# Should fail gracefully with clear error message
```

### Missing Dependencies

```bash
# Test without Playwright browsers
# Should provide clear installation instructions
```

## Automated Testing

### CI/CD Pipeline Tests

For continuous integration, create tests that:

1. **Don't require external credentials**
2. **Use mock services** for ImageKit
3. **Test core functionality** without network dependencies

### Example Mock Test

```python
def test_screenshot_service_mock():
    """Test screenshot service with mocked browser."""
    with patch('playwright.async_api.async_playwright') as mock_playwright:
        # Mock browser behavior
        mock_browser = AsyncMock()
        mock_playwright.return_value.start.return_value.chromium.launch.return_value = mock_browser
        
        # Test service initialization
        service = ScreenshotService(test_config)
        result = await service.initialize_browser()
        
        assert result is True
        mock_browser.launch.assert_called_once()
```

## Test Environment Setup

### Development Environment

```bash
# Full setup with all features
cp .env.example .env
# Edit .env with real credentials
playwright install chromium
uv sync
```

### CI Environment

```bash
# Minimal setup for automated testing
export SCREENSHOT_ENABLED=false
uv sync
# Run tests without external dependencies
```

### Docker Testing

```dockerfile
FROM python:3.13
RUN pip install uv
COPY . /app
WORKDIR /app
RUN uv sync
RUN playwright install chromium
CMD ["python", "tests/test_screenshot.py"]
```

## Troubleshooting Guide

### Common Test Failures

#### "Browser not found"

```bash
playwright install chromium
```

#### "ImageKit client not configured"

```bash
# Check .env file exists and has correct format
cat .env | grep IMAGEKIT
```

#### "Screenshot file is empty"

```bash
# Test with visible browser
PLAYWRIGHT_HEADLESS=false uv run python tests/test_screenshot.py
```

#### "Upload returns 16 bytes"

```bash
# This was a bug in older versions, should be fixed
# If still occurring, check file reading logic
```

### Getting Help

1. **Check logs** in `logs/` directory
2. **Run with verbose flag** `--verbose`
3. **Test individual components** separately
4. **Check GitHub issues** for similar problems
5. **Create new issue** with full error details

## Best Practices

### Writing New Tests

1. **Test one thing at a time**
2. **Use descriptive test names**
3. **Clean up after tests** (delete temp files)
4. **Mock external dependencies** when possible
5. **Include both success and failure cases**

### Running Tests Regularly

1. **Before committing changes**
2. **After updating dependencies**
3. **When adding new features**
4. **Before releasing new versions**

This comprehensive testing approach ensures the scraper works reliably across different environments and use cases.
