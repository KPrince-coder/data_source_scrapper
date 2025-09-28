import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure the project root is in the path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_reports import generate_report_for_combination
from restructure_questions import restructure_json

# Define configuration
BASE_URL = "https://kuulchat.com/bece/questions/"

AVAILABLE_SUBJECTS = [
    "science",
    "mathematics",
    "english",
    "social-studies",
]


def generate_url(subject: str, year: str) -> str:
    """Generate the full URL for a subject and year combination"""
    return f"{BASE_URL}{subject}-{year}/"


DEFAULT_SUBJECT = "science"
DEFAULT_YEAR = "2022"
CURRENT_YEAR = (
    datetime.now().year
)  # Update this yearly or use datetime to get current year


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

    successful_combinations = []
    failed_combinations = []

    # Process each combination in a separate Python process
    for combo in combinations:
        subject, year = combo["subject"], combo["year"]
        url = combo["url"]
        print(f"\nProcessing {subject.title()} {year}")
        print(f"URL: {url}")

        # Configure unique filenames for this combination
        temp_json_file = Path(f"temp_{subject}_{year}.json")
        temp_csv_file = Path(f"temp_{subject}_{year}.csv")

        # Create a temporary script for this combination
        temp_script = f"""
import sys
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
sys.path.insert(0, "{str(Path(__file__).resolve().parent)}")
from main import KuulchatSpider

# Configure Scrapy settings
settings = get_project_settings()
settings.set(
    "FEEDS",
    {{
        "{str(temp_json_file)}": {{
            "format": "json",
            "overwrite": True,
            "indent": 2,
        }},
        "{str(temp_csv_file)}": {{"format": "csv", "overwrite": True}},
    }},
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

process = CrawlerProcess(settings)
process.crawl(KuulchatSpider, start_urls=["{url}"])
process.start()
        """

        temp_script_file = Path(f"temp_spider_{subject}_{year}.py")
        try:
            # Write temporary script
            with open(temp_script_file, "w") as f:
                f.write(temp_script)

            # Run spider in a separate process
            import subprocess

            result = subprocess.run(
                [sys.executable, str(temp_script_file)],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                print(f"\nScrapy extraction completed for {subject.title()} {year}")

                final_output_dir = Path(base_output_dir) / f"{subject}_{year}"
                try:
                    # Restructure and clean up
                    restructure_json(
                        input_file=str(temp_json_file),
                        subject=subject,
                        year=year,
                        output_dir=final_output_dir,
                    )

                    # Generate image download report
                    generate_report_for_combination(subject, year, base_output_dir)
                    successful_combinations.append((subject, year))

                except Exception as e:
                    print(f"Error during post-processing: {e}")
                    failed_combinations.append((subject, year))
            else:
                print(f"Error running spider for {subject.title()} {year}:")
                print(result.stderr)
                failed_combinations.append((subject, year))

        except Exception as e:
            print(f"Error processing {subject.title()} {year}: {e}")
            failed_combinations.append((subject, year))

        finally:
            # Clean up temporary files
            for file in [temp_json_file, temp_csv_file, temp_script_file]:
                try:
                    if file.exists():
                        os.remove(file)
                except Exception as e:
                    print(
                        f"Warning: Could not remove temporary file {file}: {e}"
                    )  # Get the number of failed combinations
    failed = len(failed_combinations)

    # Print detailed processing summary
    print("\n" + "=" * 60)
    print(" " * 20 + "PROCESSING SUMMARY")
    print("=" * 60)

    if len(combinations) == 1:
        # Single subject/year processing
        subject, year = combinations[0]["subject"], combinations[0]["year"]
        if successful_combinations:
            print(f"\n✅ Successfully processed {subject.title()} {year}")
            print(f"   Output directory: {base_output_dir}/{subject}_{year}")
            print("   Data files:")
            print(f"   • {subject}_{year}.json")
            print(f"   • {subject}_{year}_metadata.json")
            print(f"   • {subject}_{year}.csv")
        else:
            print(f"\n❌ Failed to process {subject.title()} {year}")
    else:
        # Batch processing summary
        print(f"\nProcessed {total_combinations} subject-year combinations")

        if successful_combinations:
            print("\n✅ Successfully processed:")
            for subject, year in successful_combinations:
                print(f"\n   • {subject.title()} {year}")
                print(f"     Output directory: {base_output_dir}/{subject}_{year}")
                print("     Data files:")
                print(f"     • {subject}_{year}.json")
                print(f"     • {subject}_{year}_metadata.json")
                print(f"     • {subject}_{year}.csv")

        if failed_combinations:
            print("\n❌ Failed to process:")
            for subject, year in failed_combinations:
                print(f"   • {subject.title()} {year}")

    print("\n" + "=" * 60)

    return failed == 0


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Run Kuulchat Educational Content Spider",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_spider.py                                        # Run with defaults (science, 2022)
  python run_spider.py -s mathematics -y 2021                # Single subject, single year
  python run_spider.py -S science,mathematics -Y 2020-2022   # Multiple subjects, multiple years
  python run_spider.py -s english -Y 2023-2025               # Single subject, multiple years
  python run_spider.py -S science,mathematics -y 2025         # Multiple subjects, single year
  python run_spider.py -Y 2021-2023                           # Default subject (science), multiple years
  python run_spider.py -S science,mathematics -Y 2020-2022 -o my_data  # Custom output directory
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

    # Initialize subjects and years lists
    subjects = []
    years = []

    # Handle subjects (either -s or -S)
    if args.subjects:  # -S/--subjects was used
        subjects = parse_subjects(args.subjects)
    if args.subject and not subjects:  # -s/--subject was used and -S wasn't
        subjects = [args.subject]
    if not subjects:  # Neither -s nor -S was used
        subjects = [DEFAULT_SUBJECT]

    # Handle years (either -y or -Y)
    if args.years:  # -Y/--years was used
        years = parse_year_range(args.years)
    if args.year and not years:  # -y/--year was used and -Y wasn't
        years = [args.year]
    if not years:  # Neither -y nor -Y was used
        years = [DEFAULT_YEAR]

    # Validate that we have both subjects and years
    if not subjects or not years:
        print("Error: No valid subjects or years provided")
        sys.exit(1)

    # Run the spider with the collected subjects and years
    success = run_batch_spider(subjects, years, args.output, args.list_urls)

    if not success:
        sys.exit(1)

    if not args.list_urls:
        print("\nFull process completed successfully!")


if __name__ == "__main__":
    main()
