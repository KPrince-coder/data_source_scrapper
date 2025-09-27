import argparse
import os
import sys
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Ensure the project root is in the path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_reports import generate_report_for_combination
from main import KuulchatSpider  # Import the spider directly from main.py
from restructure_questions import restructure_json

# Define configuration
BASE_URL = "https://kuulchat.com/bece/questions/"

AVAILABLE_SUBJECTS = [
    "science",
    "mathematics",
    "english",
    "social-studies",
    "ict",
    "integrated-science",
    "religious-and-moral-education",
]


def generate_url(subject: str, year: str) -> str:
    """Generate the full URL for a subject and year combination"""
    return f"{BASE_URL}{subject}-{year}/"


DEFAULT_SUBJECT = "science"
DEFAULT_YEAR = "2022"
CURRENT_YEAR = 2025  # Update this yearly or use datetime to get current year


def validate_year(year: str) -> bool:
    """Validate that the year is within reasonable bounds (e.g., 2000-current)"""
    try:
        year_int = int(year)
        if year_int < 2000 or year_int > CURRENT_YEAR:
            print(
                f"Error: Year {year} is outside the valid range (2000-{CURRENT_YEAR})"
            )
            return False
        return True
    except ValueError:
        print(f"Error: Invalid year format '{year}'. Please use YYYY format.")
        return False


def validate_subject(subject: str) -> bool:
    """Validate that the subject exists"""
    if subject not in AVAILABLE_SUBJECTS:
        print(f"Error: Subject '{subject}' not found.")
        print(f"Available subjects: {', '.join(AVAILABLE_SUBJECTS)}")
        return False
    return True


def validate_subject_year(subject: str, year: str) -> bool:
    """Validate subject and year combination"""
    return validate_subject(subject) and validate_year(year)


def list_available_subjects():
    """List all available subjects and show example URLs"""
    print("\nAvailable subjects:")
    print("=" * 40)
    for subject in sorted(AVAILABLE_SUBJECTS):
        print(f"\nSubject: {subject.title()}")
        example_year = CURRENT_YEAR - 1  # Use previous year as example
        example_url = generate_url(subject, str(example_year))
        print(f"Example URL: {example_url}")

    print("\nValid year range: 2000-{CURRENT_YEAR}")
    print("\nExample commands:")
    print("  Single subject/year:   python run_spider.py -s science -y 2022")
    print(
        "  Multiple subjects:     python run_spider.py -S science,mathematics -Y 2020-2022"
    )
    print(
        "  List all URLs:        python run_spider.py -S science,english -Y 2020-2022 --list-urls"
    )


def run_spider_for_subject(
    subject: str, year: str, base_output_dir: str = "data", dry_run: bool = False
):
    """
    Run the spider for a specific subject and year, then restructure and clean up.

    Args:
        subject: Subject name
        year: Year
        base_output_dir: Base directory for all output (e.g., "data")
        dry_run: If True, only check URL validity without running the spider
    """
    # Use the batch processing function with a single combination
    return run_batch_spider([subject], [year], base_output_dir, dry_run)


def parse_year_range(year_range: str) -> list[str]:
    """Parse year range string into list of years"""
    if "-" in year_range:
        start_year, end_year = year_range.split("-")
        try:
            years = list(range(int(start_year), int(end_year) + 1))
            return [str(year) for year in years]
        except ValueError:
            print(
                f"Error: Invalid year range format '{year_range}'. Use YYYY-YYYY format."
            )
            return []
    return [year_range]  # Single year


def parse_subjects(subjects: str) -> list[str]:
    """Parse comma-separated subject list"""
    return [s.strip() for s in subjects.split(",")]


def run_batch_spider(
    subjects: list[str], years: list[str], base_output_dir: str, dry_run: bool = False
):
    """Run spider for multiple subject-year combinations in a single Scrapy process"""
    total_combinations = len(subjects) * len(years)
    successful = 0
    failed = 0
    combinations = []

    print(f"\nProcessing {total_combinations} subject-year combinations...")

    # First validate all combinations and collect URLs
    for subject in subjects:
        for year in years:
            if not validate_subject_year(subject, year):
                failed += 1
                continue
            url = generate_url(subject, year)
            combinations.append({"subject": subject, "year": year, "url": url})

    if dry_run:
        print("\nURLs to be processed:")
        for combo in combinations:
            print(f"Subject: {combo['subject']}, Year: {combo['year']}")
            print(f"URL: {combo['url']}\n")
        return True

    if not combinations:
        print("No valid combinations to process.")
        return False

    # Configure Scrapy settings
    settings = get_project_settings()
    temp_json_input_file = Path("bece_questions.json")
    temp_csv_input_file = Path("bece_questions.csv")

    settings.set(
        "FEEDS",
        {
            str(temp_json_input_file): {
                "format": "json",
                "overwrite": True,
                "indent": 2,
            },
            str(temp_csv_input_file): {"format": "csv", "overwrite": True},
        },
        priority="cmdline",
    )

    settings.set("LOG_LEVEL", "INFO")
    settings.set(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    )
    settings.set("DOWNLOAD_DELAY", 2)
    settings.set("RANDOMIZE_DOWNLOAD_DELAY", True)
    settings.set("CONCURRENT_REQUESTS", 1)
    settings.set("ROBOTSTXT_OBEY", True)

    # Create a single CrawlerProcess for all URLs
    process = CrawlerProcess(settings)

    # Start URLs for the spider
    start_urls = [combo["url"] for combo in combinations]

    # Run the spider with all URLs
    process.crawl(KuulchatSpider, start_urls=start_urls)
    process.start()  # The script will block here until all crawling is finished

    print("\nScrapy extraction completed for all URLs")

    # Post-processing for each combination
    if temp_json_input_file.exists():
        for combo in combinations:
            subject, year = combo["subject"], combo["year"]
            print(f"\nPost-processing for {subject.title()} {year}")

            final_output_dir = Path(base_output_dir) / f"{subject}_{year}"

            try:
                # Restructure and clean up
                restructure_json(
                    input_file=str(temp_json_input_file),
                    subject=subject,
                    year=year,
                    output_dir=final_output_dir,
                )

                # Generate image download report
                generate_report_for_combination(subject, year, base_output_dir)
                successful += 1

            except Exception as e:
                print(f"Error during post-processing: {e}")
                failed += 1

        # Cleanup intermediate files
        if temp_json_input_file.exists():
            os.remove(temp_json_input_file)
        if temp_csv_input_file.exists():
            os.remove(temp_csv_input_file)

    print("\nBatch processing complete!")
    print(f"Total combinations: {total_combinations}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    return failed == 0


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Run Kuulchat Educational Content Spider",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_spider.py                                        # Run with defaults (science 2022)
  python run_spider.py -s mathematics -y 2021                # Single subject/year
  python run_spider.py -S science,mathematics -Y 2020-2022   # Multiple subjects/years
  python run_spider.py --list                                # List available subjects
  python run_spider.py -S science,english -Y 2020-2022 --list-urls  # Preview URLs
        """,
    )

    # Single subject/year arguments
    parser.add_argument(
        "-s",
        "--subject",
        default=DEFAULT_SUBJECT,
        help=f"Subject to scrape (default: {DEFAULT_SUBJECT})",
    )

    parser.add_argument(
        "-y",
        "--year",
        default=DEFAULT_YEAR,
        help=f"Year to scrape (default: {DEFAULT_YEAR})",
    )

    # Batch processing arguments
    parser.add_argument(
        "-S",
        "--subjects",
        help="Comma-separated list of subjects to scrape (e.g., science,mathematics)",
    )

    parser.add_argument(
        "-Y",
        "--years",
        help="Year or year range to scrape (e.g., 2020 or 2019-2022)",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="data",  # Default to 'data' directory
        help="Base output directory (default: data)",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available subjects and years",
    )

    parser.add_argument(
        "--list-urls",
        action="store_true",
        help="List URLs that would be scraped without actually scraping",
    )

    args = parser.parse_args()

    # Handle list command
    if args.list:
        list_available_subjects()
        return

    # Handle batch processing
    if args.subjects or args.years:
        if not args.subjects or not args.years:
            print(
                "Error: Both -S/--subjects and -Y/--years must be provided for batch processing"
            )
            sys.exit(1)

        subjects = parse_subjects(args.subjects)
        years = parse_year_range(args.years)

        if not subjects or not years:
            sys.exit(1)

        success = run_batch_spider(subjects, years, args.output, args.list_urls)
    else:
        # Single subject/year processing
        success = run_spider_for_subject(
            args.subject, args.year, args.output, args.list_urls
        )

    if not success:
        sys.exit(1)

    if not args.list_urls:
        print("\nFull process completed successfully!")


if __name__ == "__main__":
    main()
