"""
Image Download and Management System for Educational Content

This module handles downloading, organizing, and managing educational diagrams
referenced in the scraped question data.
"""

import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Tuple


class ImageDownloader:
    """Handles downloading and organizing educational images"""

    def __init__(self, subject: str, year: str, base_output_dir: Path):
        """
        Initialize the image downloader

        Args:
            subject: Subject name (e.g., "science")
            year: Year (e.g., "2022")
            base_output_dir: Base directory for the subject/year data (e.g., data/science_2022)
        """
        self.subject = subject
        self.year = year
        self.base_output_dir = base_output_dir
        self.images_dir = self.base_output_dir / "images"

        # Create images directory if it doesn't exist
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Track downloaded images to avoid duplicates
        self.downloaded_images: dict[str, str] = {}

    def get_file_extension(self, url: str) -> str:
        """Extract file extension from URL"""
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        _, ext = os.path.splitext(path)
        return ext.lower() if ext else ".jpg"

    def generate_filename(
        self, url: str, question_type: str, question_number: int, index: int = 0
    ) -> str:
        """
        Generate a descriptive filename for the image

        Args:
            url: Original image URL
            question_type: 'objectives' or 'theory'
            question_number: Question number
            index: Index if multiple images for same question

        Returns:
            Generated filename
        """
        ext = self.get_file_extension(url)

        if index == 0:
            return f"q{question_number}_diagram{ext}"
        else:
            return f"q{question_number}_diagram_{index + 1}{ext}"

    def download_image(self, url: str, filepath: Path) -> bool:
        """
        Download an image from URL to filepath

        Args:
            url: Image URL to download
            filepath: Local filepath to save the image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Download the image
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req) as response:
                with open(filepath, "wb") as f:
                    f.write(response.read())

            print(f"Downloaded: {url} -> {filepath}")
            return True

        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
            return False

    def process_question_images(
        self, question: dict[Any, Any], question_type: str
    ) -> list[str]:
        """
        Process and download images for a single question

        Args:
            question: Question data dictionary
            question_type: The type of question (e.g., "objectives", "theory")

        Returns:
            List of local file paths for downloaded images
        """
        if not question.get("diagrams"):
            return []

        question_number = question.get("number", 0)

        # Determine target directory within the images folder
        target_dir = self.images_dir / question_type / f"question_{question_number}"

        downloaded_paths = []

        for index, image_url in enumerate(question["diagrams"]):
            # Skip if already downloaded
            if image_url in self.downloaded_images:
                downloaded_paths.append(self.downloaded_images[image_url])
                continue

            # Generate filename
            filename = self.generate_filename(
                image_url, question_type, question_number, index
            )
            filepath = target_dir / filename

            # Download the image
            if self.download_image(image_url, filepath):
                # Store the local path, but don't modify the original question's diagrams list
                relative_filepath = filepath.relative_to(self.base_output_dir)
                self.downloaded_images[image_url] = str(relative_filepath)
                downloaded_paths.append(str(relative_filepath))

        return downloaded_paths

    def download_and_update_images(
        self, questions_data: dict[str, list[dict[Any, Any]]]
    ) -> Tuple[dict[str, Any], dict[str, list[dict[Any, Any]]]]:
        """
        Download all images from the restructured questions data and update paths.

        Args:
            questions_data: Restructured questions data (grouped by type)

        Returns:
            A tuple containing:
            - Summary statistics of the download process
            - The original questions data (not modified with local image paths)
        """
        stats = {
            "total_questions": 0,
            "questions_with_images": 0,
            "total_images_expected": 0,  # Renamed for clarity
            "downloaded_images_count": 0,  # Renamed for clarity
            "failed_downloads": 0,
            "objective_questions": 0,
            "theory_questions": 0,
            "updated_questions_json": False,  # No longer updating the questions_json directly
            "downloaded_image_map": {},  # New: stores source_url -> local_path
        }

        # Create a deep copy to avoid modifying the original questions_data
        # This is important because we want to preserve remote URLs in the JSON/CSV output
        # However, the download process still needs to iterate through the diagrams
        # to perform the actual download.

        # Iterate through a copy for stats, but don't modify the original
        for q_type, questions_list in questions_data.items():
            for question in questions_list:
                stats["total_questions"] += 1
                if q_type == "objectives":
                    stats["objective_questions"] += 1
                elif q_type == "theory":
                    stats["theory_questions"] += 1

                if question.get("diagrams"):
                    # This counts questions that *had diagrams listed*, not necessarily downloaded
                    stats["questions_with_images"] += 1
                    stats["total_images_expected"] += len(question["diagrams"])

                    # Download images for this question
                    downloaded_paths = self.process_question_images(question, q_type)

                    stats["downloaded_images_count"] += len(downloaded_paths)
                    stats["failed_downloads"] += len(question["diagrams"]) - len(
                        downloaded_paths
                    )

        # Add the full map of downloaded images to stats
        stats["downloaded_image_map"] = self.downloaded_images

        stats["updated_questions_json"] = (
            False  # Confirming no direct update to questions_json
        )
        return (
            stats,
            questions_data,
        )  # Return original questions_data, not a modified one
