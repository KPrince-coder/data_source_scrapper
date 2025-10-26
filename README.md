# BECE Questions Data Scraper

A powerful web scraping tool designed to extract BECE (Basic Education Certificate Examination) questions and related content from Kuulchat.com. This tool supports batch processing of multiple subjects and years, with automatic image downloading and data structuring capabilities.

## Features

- 🔍 **Multi-subject Support**: Scrapes questions from various BECE subjects including:
  - Science
  - Mathematics
  - English
  - Social Studies
  - ICT
  - Integrated Science
  - Religious and Moral Education

- 📅 **Flexible Year Range**:
  - Supports any year from 2000 to present
  - Can process single years or year ranges
  - Batch processing for multiple years

- 🚀 **Advanced Processing**:
  - Automated image downloading and organization
  - JSON and CSV data output
  - Metadata generation
  - Detailed processing reports

- 📸 **Screenshot & PDF Integration** (New!):
  - Automatic page screenshot capture using Playwright
  - PDF conversion and cloud storage via ImageKit
  - PDF URLs embedded in JSON and CSV output
  - Visual archive of question pages

- 📊 **Organized Output Structure**:

  ```text
  data/
  ├── subject_year/
  │   ├── subject_year.json         # Main data file (with PDF URL)
  │   ├── subject_year_metadata.json # Metadata
  │   ├── subject_year.csv          # CSV format (with PDF URL)
  │   ├── images/                   # Downloaded images
  │   │   ├── objectives/
  │   │   └── theory/
  │   └── reports/                  # Processing reports
  ```

## Screenshot & PDF Features

The scraper now includes optional screenshot and PDF generation capabilities:

- **Automatic Screenshots**: Captures full-page screenshots of question pages
- **PDF Storage**: Converts screenshots to PDFs and uploads to ImageKit cloud storage
- **URL Embedding**: Adds PDF URLs to your JSON and CSV files for easy reference
- **Visual Archive**: Maintains a complete visual record alongside structured data

### Setup Screenshot Functionality

1. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

2. **Configure ImageKit** (see [SCREENSHOT_SETUP.md](SCREENSHOT_SETUP.md) for detailed instructions):
   - Create a free ImageKit account at [imagekit.io](https://imagekit.io/)
   - Get your API credentials from the dashboard
   - Add credentials to `.env` file:
     ```env
     IMAGEKIT_PUBLIC_KEY=your_public_key
     IMAGEKIT_PRIVATE_KEY=your_private_key
     IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id
     ```

3. **Run with screenshots enabled**:
   ```bash
   uv run python run_spider.py -s science -y 2022
   ```

### Screenshot Output Examples

**JSON with PDF URL**:
```json
{
  "page_screenshot_pdf": "https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026.pdf",
  "objectives": [...],
  "theory": [...]
}
```

**CSV with PDF URL**:
```csv
page_screenshot_pdf,type,number,question,...
https://ik.imagekit.io/your_id/screenshots/science/2022/science_2022_20241026.pdf,objectives,1,"What is...",...
```

For complete setup instructions, see [SCREENSHOT_SETUP.md](SCREENSHOT_SETUP.md).

  ```

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd data_source_scraper
   ```

2. Create and activate a virtual environment:
   `uv` automatically creates environment (.venv) for you. Activating it is optional but if you want to activate it the use the command below.

   ```bash
   .venv\Scripts\activate     # Windows
   
   source .venv/bin/activate  # Linux/MacOS
   ```

   If you you manually activates the .venv, then you would not need to use `uv run` in front of command like 'python run_spider.py -s science -y 2022'

3. Install dependencies:

   ```bash
   uv sync
   ```

## Usage

### Basic Usage

1. Single subject and year:

   ```bash
   uv run python run_spider.py -s science -y 2022
   ```

2. Multiple subjects:

   ```bash
   uv run python run_spider.py -S science,mathematics -y 2022
   ```

3. Year range:

   ```bash
   uv run python run_spider.py -s english -Y 2020-2025
   ```

4. Multiple subjects and years:

   ```bash
   uv run python run_spider.py -S science,english,mathematics -Y 2020-2025
   ```

### Command Line Options

```text
usage: run_spider.py [-h] [-s SUBJECT] [-y YEAR] [-S SUBJECTS] [-Y YEARS]
                     [-o OUTPUT] [--list] [--list-urls] [--no-screenshots] [-v]

Run Kuulchat Educational Content Spider

optional arguments:
  -h, --help            Show this help message and exit
  -s, --subject         Subject to scrape (default: science)
  -y, --year           Year to scrape (default: 2022)
  -S, --subjects       Comma-separated list of subjects
  -Y, --years         Year or year range (e.g., 2020 or 2019-2022)
  -o, --output        Base output directory (default: data)
  --list              List available subjects and years
  --list-urls         Preview URLs without scraping
  --no-screenshots    Disable screenshot and PDF generation
  -v, --verbose       Enable verbose logging (DEBUG level)
```

### Advanced Features

1. List available subjects and example URLs:

   ```bash
   uv run python run_spider.py --list
   ```

2. Preview URLs without scraping:

   ```bash
   uv run python run_spider.py -S science,english -Y 2024-2025 --list-urls
   ```

3. Custom output directory:

   ```bash
   uv run python run_spider.py -s science -y 2022 -o custom_data
   ```

4. Disable screenshots (faster processing):

   ```bash
   uv run python run_spider.py -s science -y 2022 --no-screenshots
   ```

5. Enable verbose logging:

   ```bash
   uv run python run_spider.py -s science -y 2022 --verbose
   ```

### Output Structure

Each subject-year combination creates its own directory with:

- `subject_year.json`: Main data file containing questions and answers
- `subject_year_metadata.json`: Metadata about the scraping process
- `subject_year.csv`: Data in CSV format
- `images/`: Directory containing downloaded images
  - `objectives/`: Images for objective questions
  - `theory/`: Images for theory questions
- `reports/`: Contains processing and download reports

## Error Handling

The scraper includes robust error handling:

- Validates subjects and years before processing
- Handles non-existent URLs gracefully
- Provides detailed feedback on failures
- Continues batch processing even if individual items fail

## Processing Summary

After completion, you'll see a detailed processing summary:

```text
============================================================
                    PROCESSING SUMMARY
============================================================

✅ Successfully processed:

   • Science 2024
     Output directory: data/science_2024
     Data files:
     • science_2024.json
     • science_2024_metadata.json
     • science_2024.csv

[...additional processed items...]

============================================================
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
