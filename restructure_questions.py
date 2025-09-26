import json
from collections import defaultdict


def restructure_json(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    restructured_data = defaultdict(list)

    for question in data:
        question_type = question.get("type")
        if question_type == "mcq":
            question_type = "objectives"
        if question_type:
            # Create a copy to avoid modifying the original object in the loop
            cleaned_question = question.copy()
            # Remove "section" and "type" keys
            cleaned_question.pop("section", None)
            cleaned_question.pop("type", None)
            restructured_data[question_type].append(cleaned_question)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(restructured_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    input_json_file = "bece_questions.json"
    output_json_file = "bece_questions_restructured.json"
    restructure_json(input_json_file, output_json_file)
    print(f"Successfully restructured '{input_json_file}' to '{output_json_file}'")
