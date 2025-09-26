import json
import os
from collections import defaultdict
from datetime import datetime


def restructure_json(input_file, subject, year, output_dir):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    restructured_data = defaultdict(list)

    total_questions = 0
    objective_questions = 0
    theory_questions = 0
    questions_with_diagrams = defaultdict(int)
    questions_with_solutions = defaultdict(int)

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

    # Write restructured questions JSON
    output_questions_path = os.path.join(output_dir, "questions.json")
    with open(output_questions_path, "w", encoding="utf-8") as f:
        json.dump(restructured_data, f, indent=2, ensure_ascii=False)

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
            "year": year,
            "source_url": f"https://kuulchat.com/bece/questions/{subject}-{year}/",  # Placeholder, adjust if needed
            "spider_reason": "restructured",
        },
        "file_structure": {
            "questions_json": "questions.json",
            "questions_csv": "questions.csv",  # Assuming CSV will be generated later
            "images": "images/",  # Assuming images will be moved/downloaded later
            "reports": "reports/",  # Assuming reports will be generated later
        },
        "format_version": "2.0",
    }

    output_metadata_path = os.path.join(output_dir, "metadata.json")
    with open(output_metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(
        f"Successfully restructured '{input_file}' to '{output_questions_path}' and created metadata at '{output_metadata_path}'"
    )


if __name__ == "__main__":
    input_json_file = "bece_questions.json"
    subject_name = "science"
    year_name = "2022"
    output_directory = os.path.join("data", f"{subject_name}_{year_name}")

    restructure_json(input_json_file, subject_name, year_name, output_directory)
