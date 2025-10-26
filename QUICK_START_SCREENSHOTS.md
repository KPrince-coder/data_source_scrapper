# Quick Start: Screenshot & PDF Integration

Get started with screenshot and PDF generation in 5 minutes!

## Prerequisites

- Python 3.13+ installed
- Project dependencies installed (`uv sync`)

## Quick Setup (3 Steps)

### 1. Install Playwright Browser

```bash
playwright install chromium
```

### 2. Get ImageKit Credentials

1. Sign up at [imagekit.io](https://imagekit.io/) (free)
2. Go to Dashboard → Developer Options → API Keys
3. Copy your credentials

### 3. Configure Environment

Create a `.env` file in the project root:

```env
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id
SCREENSHOT_ENABLED=true
```

## Usage

### Run with Screenshots (Default)

```bash
uv run python run_spider.py -s science -y 2022
```

Output includes PDF URL in JSON and CSV files!

### Run without Screenshots

```bash
uv run python run_spider.py -s science -y 2022 --no-screenshots
```

### Batch Processing with Screenshots

```bash
uv run python run_spider.py -S science,mathematics -Y 2020-2022
```

## What You Get

### Enhanced JSON Output

```json
{
  "page_screenshot_pdf": "https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026.pdf",
  "objectives": [...],
  "theory": [...]
}
```

### Enhanced CSV Output

New `page_screenshot_pdf` column with direct links to PDFs.

### ImageKit Dashboard

View all your PDFs at: `https://imagekit.io/dashboard`

Organized in folders: `/screenshots/{subject}/{year}/`

## Troubleshooting

### "ImageKit client not configured"

Check your `.env` file exists and has correct credentials.

### "Failed to initialize browser"

Run: `playwright install chromium`

### Screenshots disabled automatically

Check logs - likely missing ImageKit credentials.

## Performance

- Adds ~10-20 seconds per subject-year combination
- Free ImageKit tier: 20GB bandwidth/month (plenty for typical usage)
- Screenshots are optional - disable with `--no-screenshots` for faster processing

## Need Help?

- Full setup guide: [SCREENSHOT_SETUP.md](SCREENSHOT_SETUP.md)
- Main documentation: [README.md](README.md)
- Check logs in `logs/` directory

## Example Workflow

```bash
# 1. Install browser (one-time)
playwright install chromium

# 2. Configure .env with ImageKit credentials

# 3. Test with single subject
uv run python run_spider.py -s science -y 2022

# 4. Check output
# - JSON file has page_screenshot_pdf field
# - CSV file has page_screenshot_pdf column
# - PDF viewable in ImageKit dashboard

# 5. Run batch processing
uv run python run_spider.py -S science,mathematics,english -Y 2022-2024
```

That's it! You now have visual archives of all your scraped pages. 🎉