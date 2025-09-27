import json
import os
from datetime import datetime


def get_subject_year_combinations(data_dir):
    """Identifies all subject_year combinations from the data directory."""
    combinations = []
    for entry in os.listdir(data_dir):
        if os.path.isdir(os.path.join(data_dir, entry)) and "_" in entry:
            parts = entry.split("_")
            if len(parts) > 1 and parts[-1].isdigit():
                subject = "_".join(parts[:-1])
                year = parts[-1]
                combinations.append((subject, year))
    return combinations


def generate_report_for_combination(subject, year, base_data_dir):
    """Generates an image download report for a given subject and year."""
    subject_year_dir = os.path.join(base_data_dir, f"{subject}_{year}")
    metadata_file_path = os.path.join(
        subject_year_dir, f"{subject}_{year}_metadata.json"
    )

    if not os.path.exists(metadata_file_path):
        print(f"Metadata file not found for {subject} {year}: {metadata_file_path}")
        return

    with open(metadata_file_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    spider_stats = metadata.get("spider_stats", {})
    image_download_stats = spider_stats.get("image_download_stats", {})

    total_questions = spider_stats.get("total_questions", 0)
    questions_with_images_objective = spider_stats.get(
        "questions_with_diagrams", {}
    ).get("objectives", 0)
    questions_with_images_theory = spider_stats.get("questions_with_diagrams", {}).get(
        "theory", 0
    )

    total_images_expected = image_download_stats.get("total_images_expected", 0)
    successfully_downloaded_count = image_download_stats.get(
        "downloaded_images_count", 0
    )
    failed_downloads_count = image_download_stats.get("failed_downloads", 0)
    downloaded_image_map = image_download_stats.get("downloaded_image_map", {})

    success_rate = (
        (successfully_downloaded_count / total_images_expected * 100)
        if total_images_expected > 0
        else 0
    )

    # Generate report content
    report_content = []
    report_content.append(
        f"Image Download Report for {subject.replace('_', ' ').title()} {year}"
    )
    report_content.append(f"Generated on: {datetime.now().isoformat()}")
    report_content.append("\nSummary:")
    report_content.append(f"  Total Questions: {total_questions}")
    report_content.append("  Questions with Images:")
    report_content.append(f"    Objective Questions: {questions_with_images_objective}")
    report_content.append(f"    Theory Questions: {questions_with_images_theory}")
    report_content.append(f"  Total Images Expected: {total_images_expected}")
    report_content.append(f"  Successfully Downloaded: {successfully_downloaded_count}")
    report_content.append(f"  Failed Downloads: {failed_downloads_count}")
    report_content.append(f"  Success Rate: {success_rate:.2f}%")
    report_content.append("  Images are organized in:")
    report_content.append(f"    {os.path.join('images', 'objective')}/")
    report_content.append(f"    {os.path.join('images', 'theory')}/")
    report_content.append("\nDownloaded Images:")
    for source_url, local_path in downloaded_image_map.items():
        report_content.append(f"  Downloaded: {source_url} -> {local_path}")

    # Add failed downloads for completeness (if any)
    if failed_downloads_count > 0:
        report_content.append("\nFailed Downloads (Expected but not found locally):")
        # To list failed downloads, we need the original expected URLs that are NOT in downloaded_image_map
        # This requires re-reading the original JSON or having the full expected list in metadata.
        # For now, we'll just state the count.
        report_content.append(
            f"  {failed_downloads_count} images failed to download or were not found."
        )
        report_content.append(
            "  (Detailed list of failed downloads not available in metadata for this version.)"
        )

    # Write report to file
    reports_dir = os.path.join(subject_year_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file_path = os.path.join(
        reports_dir, f"{subject}_{year}_image_download_report.txt"
    )
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))
    print(f"Report generated for {subject} {year} at {report_file_path}")


def main():
    base_data_dir = "data"
    combinations = get_subject_year_combinations(base_data_dir)

    if not combinations:
        print(f"No subject_year combinations found in {base_data_dir}")
        return

    for subject, year in combinations:
        generate_report_for_combination(subject, year, base_data_dir)


if __name__ == "__main__":
    main()
