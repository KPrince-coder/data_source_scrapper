# Screenshot and PDF Integration Setup Guide

This guide will help you set up the screenshot and PDF generation functionality for the BECE Questions Data Scraper.

## Overview

The screenshot integration captures visual representations of question pages and stores them as PDFs in ImageKit cloud storage. The PDF URLs are then embedded in your JSON and CSV output files for easy reference.

## Prerequisites

- Python 3.13 or higher
- Active ImageKit account (free tier available)
- Internet connection for ImageKit uploads

## Step 1: Install Dependencies

The required dependencies should already be in your `pyproject.toml`. Install them with:

```bash
uv sync
```

This will install:

- `playwright>=1.40.0` - Browser automation
- `imagekitio>=4.2.0` - ImageKit SDK
- `Pillow>=10.0.0` - Image processing
- `reportlab>=4.0.0` - PDF generation
- `scrapy-playwright>=0.0.44` - Scrapy integration

## Step 2: Install Playwright Browsers

Playwright requires browser binaries to be installed separately:

```bash
playwright install chromium
```

This downloads the Chromium browser that will be used for screenshots. You can also install other browsers:

```bash
# Optional: Install other browsers
playwright install firefox
playwright install webkit
```

## Step 3: Set Up ImageKit Account

### 3.1 Create ImageKit Account

1. Go to [ImageKit.io](https://imagekit.io/)
2. Sign up for a free account
3. Verify your email address

### 3.2 Get API Credentials

1. Log in to your ImageKit dashboard
2. Navigate to **Developer Options** → **API Keys**
3. Copy the following credentials:
   - **Public Key**
   - **Private Key**
   - **URL Endpoint** (format: `https://ik.imagekit.io/your_id`)

## Step 4: Configure Environment Variables

### 4.1 Create .env File

Copy the example environment file:

```bash
copy .env.example .env
```

### 4.2 Add Your ImageKit Credentials

Edit the `.env` file and add your ImageKit credentials:

```env
# ImageKit Configuration (Required)
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id

# Screenshot Configuration (Optional - defaults provided)
SCREENSHOT_ENABLED=true
PLAYWRIGHT_BROWSER=chromium
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_VIEWPORT_WIDTH=1920
PLAYWRIGHT_VIEWPORT_HEIGHT=1080
PLAYWRIGHT_TIMEOUT=30000
PLAYWRIGHT_SCREENSHOT_FORMAT=png
PLAYWRIGHT_QUALITY=90

# PDF Configuration (Optional - defaults provided)
PDF_QUALITY=95
PDF_FORMAT=A4
PDF_MARGIN_TOP=20
PDF_MARGIN_BOTTOM=20
PDF_MARGIN_LEFT=20
PDF_MARGIN_RIGHT=20
```

**Important:** Never commit your `.env` file to version control. It's already in `.gitignore`.

## Step 5: Test Configuration

Run the configuration test to verify everything is set up correctly:

```bash
uv run python -c "from config.screenshot_config import load_config; config = load_config(); print(f'Screenshot enabled: {config.enabled}'); print(f'ImageKit configured: {config.imagekit.is_configured()}')"
```

Expected output:

```
Screenshot enabled: True
ImageKit configured: True
```

## Step 6: Run Your First Screenshot

Test the screenshot functionality with a single subject and year:

```bash
uv run python run_spider.py -s science -y 2022
```

The scraper will:

1. Extract questions from the website
2. Capture a screenshot of the page
3. Convert the screenshot to PDF
4. Upload the PDF to ImageKit
5. Add the PDF URL to your JSON and CSV files

## Configuration Options

### Disable Screenshots

If you want to run the scraper without screenshots:

```bash
uv run python run_spider.py -s science -y 2022 --no-screenshots
```

Or set in `.env`:

```env
SCREENSHOT_ENABLED=false
```

### Verbose Logging

Enable detailed logging for debugging:

```bash
uv run python run_spider.py -s science -y 2022 --verbose
```

### Browser Options

Change the browser type in `.env`:

```env
PLAYWRIGHT_BROWSER=firefox  # Options: chromium, firefox, webkit
```

### Headless Mode

Run browser in visible mode (useful for debugging):

```env
PLAYWRIGHT_HEADLESS=false
```

## Output Structure

After running with screenshots enabled, your output will include:

```
data/science_2022/
├── science_2022.json          # Contains page_screenshot_pdf field
├── science_2022.csv           # Contains page_screenshot_pdf column
├── science_2022_metadata.json
├── images/
│   ├── objectives/
│   └── theory/
└── reports/
```

### JSON Structure with PDF URL

```json
{
  "page_screenshot_pdf": "https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026.pdf",
  "objectives": [...],
  "theory": [...]
}
```

### CSV Structure with PDF URL

```csv
page_screenshot_pdf,type,number,question,...
https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026.pdf,objectives,1,"What is...",...
```

## ImageKit Dashboard

View your uploaded PDFs in the ImageKit dashboard:

1. Log in to [ImageKit.io](https://imagekit.io/)
2. Navigate to **Media Library**
3. Browse to `/screenshots/{subject}/{year}/`

## Troubleshooting

### Issue: "ImageKit client not configured"

**Solution:** Verify your environment variables are set correctly in `.env`

```bash
# Check if .env file exists
dir .env

# Verify environment variables are loaded
uv run python -c "import os; print(os.getenv('IMAGEKIT_PUBLIC_KEY'))"
```

### Issue: "Failed to initialize browser"

**Solution:** Ensure Playwright browsers are installed

```bash
playwright install chromium
```

### Issue: "Screenshot capture timeout"

**Solution:** Increase timeout in `.env`

```env
PLAYWRIGHT_TIMEOUT=60000  # 60 seconds
```

### Issue: "PDF upload failed"

**Solution:** Check your internet connection and ImageKit credentials

```bash
# Test ImageKit connection
uv run python -c "from imagekitio import ImageKit; ik = ImageKit(private_key='your_key', public_key='your_key', url_endpoint='your_endpoint'); print('Connected!')"
```

### Issue: Screenshots work but data files not enriched

**Solution:** Check file permissions and paths. The enrichment service needs write access to the output directory.

## Performance Considerations

- **Screenshot capture** adds ~5-10 seconds per page
- **PDF conversion** adds ~2-3 seconds
- **ImageKit upload** depends on file size and internet speed (~3-5 seconds)
- **Total overhead**: ~10-20 seconds per subject-year combination

For batch processing, this is done sequentially to avoid overwhelming resources.

## Cost Considerations

ImageKit free tier includes:

- 20 GB bandwidth per month
- 20 GB storage
- Unlimited transformations

For typical usage (100-200 PDFs per month), the free tier should be sufficient.

## Security Best Practices

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate API keys** - Periodically regenerate keys in ImageKit dashboard
4. **Limit API key permissions** - Use read/write only, not admin keys

## Next Steps

- Read the main [README.md](README.md) for general scraper usage
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review ImageKit [documentation](https://docs.imagekit.io/) for advanced features

## Support

If you encounter issues:

1. Check the logs in `logs/` directory
2. Review this setup guide
3. Verify all prerequisites are met
4. Check ImageKit dashboard for upload status
