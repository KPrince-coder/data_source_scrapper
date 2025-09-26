"""
Image Download and Management System for Educational Content

This module handles downloading, organizing, and managing educational diagrams
referenced in the scraped question data.
"""

import os
import json
import urllib.parse
import urllib.request
import hashlib
from pathlib import Path
from typing import List, Dict, Any


class ImageDownloader:
    """Handles downloading and organizing educational images"""
    
    def __init__(self, base_dir: str = "images"):
        """
        Initialize the image downloader
        
        Args:
            base_dir: Base directory for storing downloaded images
        """
        self.base_dir = Path(base_dir)
        self.objective_dir = self.base_dir / "objective"
        self.theory_dir = self.base_dir / "theory"
        
        # Create directories if they don't exist
        self.base_dir.mkdir(exist_ok=True)
        self.objective_dir.mkdir(exist_ok=True)
        self.theory_dir.mkdir(exist_ok=True)
        
        # Track downloaded images to avoid duplicates
        self.downloaded_images = {}
        
    def get_file_extension(self, url: str) -> str:
        """Extract file extension from URL"""
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        _, ext = os.path.splitext(path)
        return ext.lower() if ext else '.jpg'
    
    def generate_filename(self, url: str, question_type: str, question_number: int, index: int = 0) -> str:
        """
        Generate a descriptive filename for the image
        
        Args:
            url: Original image URL
            question_type: 'objective' or 'theory'
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                with open(filepath, 'wb') as f:
                    f.write(response.read())
            
            print(f"Downloaded: {url} -> {filepath}")
            return True
            
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
            return False
    
    def process_question_images(self, question: Dict[Any, Any]) -> List[str]:
        """
        Process and download images for a single question
        
        Args:
            question: Question data dictionary
            
        Returns:
            List of local file paths for downloaded images
        """
        if not question.get('diagrams'):
            return []
        
        question_type = question.get('section', 'unknown')
        question_number = question.get('number', 0)
        
        # Determine target directory
        if question_type == 'objective':
            target_dir = self.objective_dir / f"question_{question_number}"
        elif question_type == 'theory':
            target_dir = self.theory_dir / f"question_{question_number}"
        else:
            target_dir = self.base_dir / "unknown" / f"question_{question_number}"
        
        downloaded_paths = []
        
        for index, image_url in enumerate(question['diagrams']):
            # Skip if already downloaded
            if image_url in self.downloaded_images:
                downloaded_paths.append(self.downloaded_images[image_url])
                continue
            
            # Generate filename
            filename = self.generate_filename(image_url, question_type, question_number, index)
            filepath = target_dir / filename
            
            # Download the image
            if self.download_image(image_url, filepath):
                self.downloaded_images[image_url] = str(filepath)
                downloaded_paths.append(str(filepath))
        
        return downloaded_paths
    
    def download_all_images(self, json_file: str) -> Dict[str, Any]:
        """
        Download all images from the questions JSON file
        
        Args:
            json_file: Path to the questions JSON file
            
        Returns:
            Summary statistics of the download process
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return {}
        
        stats = {
            'total_questions': len(questions),
            'questions_with_images': 0,
            'total_images': 0,
            'downloaded_images': 0,
            'failed_downloads': 0,
            'objective_questions': 0,
            'theory_questions': 0
        }
        
        for question in questions:
            if question.get('diagrams'):
                stats['questions_with_images'] += 1
                stats['total_images'] += len(question['diagrams'])
                
                if question.get('section') == 'objective':
                    stats['objective_questions'] += 1
                elif question.get('section') == 'theory':
                    stats['theory_questions'] += 1
                
                # Download images for this question
                downloaded_paths = self.process_question_images(question)
                stats['downloaded_images'] += len(downloaded_paths)
                stats['failed_downloads'] += len(question['diagrams']) - len(downloaded_paths)
        
        return stats
    
    def generate_download_report(self, stats: Dict[str, Any]) -> str:
        """Generate a summary report of the download process"""
        report = f"""
Image Download Report
====================

Total Questions: {stats['total_questions']}
Questions with Images: {stats['questions_with_images']}
- Objective Questions: {stats['objective_questions']}
- Theory Questions: {stats['theory_questions']}

Total Images: {stats['total_images']}
Successfully Downloaded: {stats['downloaded_images']}
Failed Downloads: {stats['failed_downloads']}

Success Rate: {(stats['downloaded_images'] / stats['total_images'] * 100):.1f}%

Images are organized in:
- {self.objective_dir}/ (Objective questions)
- {self.theory_dir}/ (Theory questions)
"""
        return report


def main():
    """Main function to run the image downloader"""
    downloader = ImageDownloader()
    
    # Download all images from the questions file
    print("Starting image download process...")
    stats = downloader.download_all_images('bece_questions.json')
    
    # Generate and display report
    report = downloader.generate_download_report(stats)
    print(report)
    
    # Save report to file
    with open('image_download_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Download complete! Report saved to 'image_download_report.txt'")


if __name__ == "__main__":
    main()
