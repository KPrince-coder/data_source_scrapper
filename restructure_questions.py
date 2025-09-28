import csv
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from image_downloader import ImageDownloader


def flatten_question(question: Dict[Any, Any], q_type: str) -> Dict[str, Any]:
    """Flattens a nested question dictionary for CSV output."""
    flat_question = {
        "type": q_type,
        "number": question.get("number"),
        "question": question.get("question"),
        "solution": question.get("solution", ""),
        "answer": question.get("answer", ""),
        "diagrams": "|".join(question.get("diagrams", [])),
    }

    # Handle options for 'objectives' type
    if q_type == "objectives" and "options" in question:
        for opt_key, opt_value in question["options"].items():
            flat_question[f"option_{opt_key}"] = opt_value

    # Handle subparts for 'theory' type
    if q_type == "theory" and "subparts" in question:
        for i, subpart in enumerate(question["subparts"]):
            flat_question[f"subpart_{i + 1}_question"] = subpart.get("question", "")
            flat_question[f"subpart_{i + 1}_solution"] = subpart.get("solution", "")
            flat_question[f"subpart_{i + 1}_answer"] = subpart.get("answer", "")
            if "subparts" in subpart:  # Nested subparts
                for j, nested_subpart in enumerate(subpart["subparts"]):
                    flat_question[f"subpart_{i + 1}_{chr(97 + j)}_question"] = (
                        nested_subpart.get("question", "")
                    )
                    flat_question[f"subpart_{i + 1}_{chr(97 + j)}_solution"] = (
                        nested_subpart.get("solution", "")
                    )
                    flat_question[f"subpart_{i + 1}_{chr(97 + j)}_answer"] = (
                        nested_subpart.get("answer", "")
                    )

    return flat_question


def restructure_json(input_file: str, subject: str, year: str, output_dir: Path):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    restructured_data = defaultdict(list)

    total_questions = 0
    objective_questions = 0
    theory_questions = 0
    questions_with_diagrams: defaultdict[str, int] = defaultdict(int)
    questions_with_solutions: defaultdict[str, int] = defaultdict(int)

    for question in data:
        total_questions += 1
        question_type = question.get("type")

        if question_type == "mcq":
            question_type = "objectives"
            objective_questions += 1
        elif question_type == "theory":
            theory_questions += 1

        if question_type:
            cleaned_question = question.copy()
            cleaned_question.pop("section", None)
            cleaned_question.pop("type", None)
            restructured_data[question_type].append(cleaned_question)

            if cleaned_question.get("diagrams"):
                questions_with_diagrams[question_type] += 1
            if cleaned_question.get("solution"):
                questions_with_solutions[question_type] += 1

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize ImageDownloader
    downloader = ImageDownloader(subject, year, output_dir)

    # Download images and update question paths
    download_stats, original_questions_data_for_output = (
        downloader.download_and_update_images(restructured_data)
    )

    # Write restructured questions JSON
    output_questions_filename = f"{subject}_{year}.json"
    output_questions_path = output_dir / output_questions_filename
    with open(output_questions_path, "w", encoding="utf-8") as f:
        json.dump(original_questions_data_for_output, f, indent=2, ensure_ascii=False)

    # Prepare data for CSV and write CSV
    flattened_data = []
    for q_type, questions_list in original_questions_data_for_output.items():
        for question in questions_list:
            flattened_data.append(flatten_question(question, q_type))

    if flattened_data:
        csv_filename = f"{subject}_{year}.csv"
        csv_path = output_dir / csv_filename

        # Determine all possible fieldnames dynamically
        all_fieldnames: set[Any] = set()
        for row in flattened_data:
            all_fieldnames.update(row.keys())

        # Sort fieldnames for consistent order, putting common fields first
        ordered_fieldnames = sorted(
            list(all_fieldnames),
            key=lambda x: (
                0
                if x in ["type", "number", "question", "solution", "answer", "diagrams"]
                else 1
                if x.startswith("option_")
                else 2
                if x.startswith("subpart_")
                else 3,
                x,
            ),
        )

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
        print(f"Successfully created CSV at '{csv_path}'")

    # Create metadata file
    metadata = {
        "subject": subject,
        "year": year,
        "extraction_date": datetime.now().isoformat(),
        "spider_stats": {
            "total_questions": total_questions,
            "objective_questions": objective_questions,
            "theory_questions": theory_questions,
            "questions_with_diagrams": dict(questions_with_diagrams),
            "questions_with_solutions": dict(questions_with_solutions),
            "subject": subject,
            "source_url": f"https://kuulchat.com/bece/questions/{subject}-{year}/",  # Placeholder, adjust if needed
            "spider_reason": "restructured",
            "image_download_stats": download_stats,  # Add image download stats
        },
        "file_structure": {
            "questions_json": output_questions_filename,
            "questions_csv": f"{subject}_{year}.csv",
            "images": "images/",  # Assuming images will be moved/downloaded later
            "reports": "reports/",  # Assuming reports will be generated later
        },
        "format_version": "2.0",
    }

    output_metadata_filename = f"{subject}_{year}_metadata.json"
    output_metadata_path = output_dir / output_metadata_filename
    with open(output_metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Move and rename image download report
    old_report_path = Path("image_download_report.txt")
    if old_report_path.exists():
        reports_dir = output_dir / "reports"
        os.makedirs(reports_dir, exist_ok=True)
        new_report_filename = f"{subject}_{year}_image_download_report.txt"
        new_report_path = reports_dir / new_report_filename
        os.rename(old_report_path, new_report_path)
        print(f"Moved and renamed image download report to '{new_report_path}'")

    print(
        f"Successfully restructured '{input_file}' to '{output_questions_path}' and created metadata at '{output_metadata_path}'"
    )
