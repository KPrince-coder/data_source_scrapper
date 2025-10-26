# Screenshot Integration Guide

This guide covers the screenshot functionality that captures visual representations of question pages and stores them in ImageKit cloud storage.

## Overview

The screenshot integration adds visual archiving capabilities to the BECE Questions Data Scraper by:

- 📸 **Capturing full-page screenshots** of question pages using Playwright
- ☁️ **Storing screenshots** as PNG images in ImageKit cloud storage  
- 🔗 **Embedding URLs** in JSON and CSV output files for easy access
- 🚀 **Automatic processing** integrated into the existing scraper workflow

## Quick Start

### 1. Install Playwright Browser

```bash
playwright install chromium
```

### 2. Configure ImageKit

1. Create a free account at [imagekit.io](https://imagekit.io/)
2. Get your API credentials from Dashboard → Developer Options → API Keys
3. Add credentials to `.env` file:

```env
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id
SCREENSHOT_ENABLED=true
```

### 3. Run with Screenshots

```bash
uv run python run_spider.py -s science -y 2022
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCREENSHOT_ENABLED` | Enable/disable screenshot functionality | `true` |
| `PLAYWRIGHT_BROWSER` | Browser type (chromium, firefox, webkit) | `chromium` |
| `PLAYWRIGHT_HEADLESS` | Run browser in headless mode | `true` |
| `PLAYWRIGHT_VIEWPORT_WIDTH` | Browser viewport width | `1920` |
| `PLAYWRIGHT_VIEWPORT_HEIGHT` | Browser viewport height | `1080` |
| `PLAYWRIGHT_TIMEOUT` | Page load timeout in milliseconds | `60000` |

### Complete .env Example

```env
# ImageKit Configuration (Required)
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id

# Screenshot Configuration (Optional)
SCREENSHOT_ENABLED=true
PLAYWRIGHT_BROWSER=chromium
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_VIEWPORT_WIDTH=1920
PLAYWRIGHT_VIEWPORT_HEIGHT=1080
PLAYWRIGHT_TIMEOUT=60000
```

## Output Structure

### Enhanced JSON Output

```json
{
  "page_screenshot": "https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026_143052.png?updatedAt=1761494123212",
  "objectives": [...],
  "theory": [...]
}
```

### Enhanced CSV Output

```csv
page_screenshot,type,number,question,...
https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026_143052.png?updatedAt=1761494123212,objectives,1,"What is...",...
```

## Command Line Usage

### Basic Usage

```bash
# With screenshots (default if configured)
uv run python run_spider.py -s science -y 2022

# Without screenshots
uv run python run_spider.py -s science -y 2022 --no-screenshots

# Batch processing with screenshots
uv run python run_spider.py -S science,mathematics -Y 2020-2022

# Verbose logging for debugging
uv run python run_spider.py -s science -y 2022 --verbose
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--no-screenshots` | Disable screenshot capture |
| `--verbose`, `-v` | Enable debug logging |

## Architecture

### Services

1. **ScreenshotService** (`services/screenshot_service.py`)
   - Manages Playwright browser automation
   - Captures full-page screenshots
   - Handles timeouts and retries

2. **ScreenshotStorageService** (`services/screenshot_storage_service.py`)
   - Uploads screenshots to ImageKit
   - Manages file organization and naming
   - Handles upload retries and error recovery

3. **DataEnrichmentService** (`services/data_enrichment_service.py`)
   - Adds screenshot URLs to JSON/CSV files
   - Creates backups before modification
   - Validates file integrity

4. **ScreenshotWorkflow** (`services/screenshot_workflow.py`)
   - Orchestrates the complete workflow
   - Coordinates all services
   - Manages cleanup and error handling

### Workflow Steps

1. **Capture**: Take full-page screenshot using Playwright
2. **Upload**: Store screenshot in ImageKit with organized folder structure
3. **Enrich**: Add screenshot URL to JSON and CSV output files

## File Organization

Screenshots are organized in ImageKit with the following structure:

```text
/screenshots/
├── science/
│   ├── 2022/
│   │   └── science_2022_20241026_143052.png
│   └── 2023/
│       └── science_2023_20241026_143052.png
├── mathematics/
│   └── 2022/
│       └── mathematics_2022_20241026_143052.png
```

### Filename Format

`{subject}_{year}_{timestamp}.png`

- **subject**: Subject name (e.g., science, mathematics)
- **year**: Year (e.g., 2022, 2023)
- **timestamp**: Upload timestamp (YYYYMMDD_HHMMSS)

## Troubleshooting

### Common Issues

#### "ImageKit client not configured"

**Solution**: Verify environment variables in `.env` file

```bash
# Check if .env file exists and has correct values
cat .env | grep IMAGEKIT
```

#### "Failed to initialize browser"

**Solution**: Install Playwright browsers

```bash
playwright install chromium
```

#### "Screenshot capture timeout"

**Solution**: Increase timeout in `.env`

```env
PLAYWRIGHT_TIMEOUT=90000  # 90 seconds
```

#### Screenshots appear corrupted or empty

**Solution**: Check browser configuration

```env
PLAYWRIGHT_HEADLESS=false  # For debugging
PLAYWRIGHT_VIEWPORT_WIDTH=1920
PLAYWRIGHT_VIEWPORT_HEIGHT=1080
```

### Testing

#### Test Screenshot Capture

```bash
uv run python tests/test_screenshot.py
```

#### Test ImageKit Upload

```bash
uv run python tests/test_upload.py
```

### Logs

Check logs in the `logs/` directory for detailed error information:

```bash
# View latest log
ls -la logs/
tail -f logs/screenshot_workflow_*.log
```

## Performance

### Timing

- Screenshot capture: ~5-10 seconds per page
- ImageKit upload: ~3-5 seconds (depends on file size and connection)
- Data enrichment: ~1-2 seconds
- **Total overhead**: ~10-20 seconds per subject-year combination

### Optimization Tips

1. **Use headless mode** for faster processing (default)
2. **Batch processing** for multiple subjects/years
3. **Disable screenshots** for faster data-only scraping with `--no-screenshots`

## ImageKit Dashboard

View and manage your screenshots:

1. Log in to [ImageKit.io](https://imagekit.io/)
2. Navigate to **Media Library**
3. Browse to `/screenshots/{subject}/{year}/`

### Features Available

- View screenshot thumbnails
- Download original files
- Delete old screenshots
- Monitor storage usage
- Access transformation URLs

## Cost Considerations

ImageKit free tier includes:

- 20 GB bandwidth per month
- 20 GB storage
- Unlimited transformations

For typical usage (100-200 screenshots per month), the free tier is sufficient.

## Security

- API keys stored in environment variables
- HTTPS-only communication with ImageKit
- No sensitive data in screenshot filenames
- Automatic cleanup of temporary files

## Integration with Existing Workflow

The screenshot functionality integrates seamlessly with the existing scraper:

1. **Non-intrusive**: Can be enabled/disabled without affecting core scraping
2. **Optional**: Graceful degradation when not configured
3. **Backward compatible**: Existing data structure preserved
4. **Error resilient**: Screenshot failures don't break data extraction

## Next Steps

- [Main README](../README.md) - General scraper documentation
- [API Reference](API_REFERENCE.md) - Detailed API documentation
- [Contributing](CONTRIBUTING.md) - Development guidelines
