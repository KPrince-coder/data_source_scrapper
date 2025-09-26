import html
import os
import re

import scrapy


class KuulchatSpider(scrapy.Spider):
    name = "kuulchat"
    start_urls = ["https://kuulchat.com/bece/questions/science-2022/"]

    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        # Decode HTML entities
        text = html.unescape(text)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_full_text(self, element):
        """Extract all text content including nested elements"""
        if not element:
            return ""
        # Get all text including from nested elements
        all_text = element.css("::text").getall()
        # Join and clean
        return self.clean_text(" ".join(all_text))

    def is_advertisement(self, element):
        """Check if an element contains advertisement content"""
        if not element:
            return False

        # Check for advertisement indicators
        text_content = self.extract_full_text(element).lower()
        ad_keywords = [
            "sponsored",
            "advertise",
            "kuulchat media",
            "kuulpay.com",
            "get a professional",
            "affordable website",
            "management system",
        ]

        return any(keyword in text_content for keyword in ad_keywords)

    def parse(self, response):
        # Extract all questions in proper order: objectives first, then theory
        all_questions = []

        # Extract objective questions first
        objective_questions = list(self.extract_objective_questions(response))
        all_questions.extend(objective_questions)

        # Extract theory questions after objectives
        theory_questions = list(self.extract_theory_questions(response))
        all_questions.extend(theory_questions)

        # Yield all questions in proper order
        for question in all_questions:
            yield question

        # Handle pagination
        next_page = response.css(
            'a.next::attr(href), .pagination a:contains("Next")::attr(href)'
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def extract_objective_questions(self, response):
        """Extract objective questions using direct HTML parsing"""
        objective_questions = []

        # Find all objective question divs - they are the direct children after OBJECTIVE TEST
        objective_section = response.css('h4.center:contains("OBJECTIVE TEST")')
        if not objective_section:
            return

        # Get the next div that contains all questions
        questions_container = objective_section[0].xpath("following-sibling::div[1]")[0]

        # Each question is in its own div
        question_divs = questions_container.css("div")

        for question_div in question_divs:
            # Skip if this contains theory questions marker
            if "THEORY QUESTIONS" in self.extract_full_text(question_div):
                break

            # Skip advertisements
            if self.is_advertisement(question_div):
                continue

            # Parse the question
            question_data = self.parse_objective_question_improved(question_div)
            if question_data:
                objective_questions.append(question_data)

        # Sort by question number
        objective_questions.sort(key=lambda x: x.get("number", 0))

        for question in objective_questions:
            yield question

    def parse_objective_question_improved(self, container):
        """Parse objective question with improved structure and answer extraction"""
        full_text = self.extract_full_text(container)

        # Look for question number pattern
        num_match = re.search(r"(\d+)\.", full_text)
        if not num_match:
            return None

        question_num = int(num_match.group(1))

        # Split content into question part and solution part
        parts = re.split(r"\s+(?:Mark|Solution)\s+", full_text, 1)
        question_part = parts[0]
        solution_part = parts[1] if len(parts) > 1 else ""

        # Extract question text (remove number and options)
        question_text = self.extract_question_stem(question_part, question_num)

        # Extract options
        options = self.extract_options_from_text(question_part)

        # Extract answer and explanation from solution
        answer_info = self.extract_answer_info(solution_part)

        # Extract all diagrams/images
        diagrams = self.extract_all_diagrams(container)

        # Only return if we have valid content
        if question_text and any(options.values()) and question_num > 0:
            result = {
                "section": "objective",
                "type": "mcq",
                "number": question_num,
                "question": question_text,
                "options": options,
                "diagrams": diagrams if diagrams else [],
            }

            # Add answer information if available
            if answer_info:
                result.update(answer_info)

            return result

        return None

    def extract_question_stem(self, question_part, question_num):
        """Extract the main question text without number and options"""
        # Remove question number
        text = re.sub(rf"^{question_num}\.?\s*", "", question_part)

        # Split at first option to get question stem
        option_split = re.split(r"\s+[A-D]\.\s+", text, 1)
        question_stem = option_split[0].strip()

        # Clean up the question stem
        question_stem = re.sub(r"\s+", " ", question_stem)

        return question_stem

    def extract_options_from_text(self, text):
        """Extract options A, B, C, D from text"""
        options = {"A": "", "B": "", "C": "", "D": ""}

        # Find all option patterns
        option_matches = re.finditer(r"([A-D])\.\s*([^A-D]*?)(?=\s+[A-D]\.|$)", text)

        for match in option_matches:
            letter = match.group(1)
            option_text = match.group(2).strip()

            # Clean up option text
            option_text = re.sub(r"\s+", " ", option_text)
            option_text = re.sub(r"\.$", "", option_text)  # Remove trailing period

            if letter in options and option_text:
                options[letter] = option_text

        return options

    def extract_answer_info(self, solution_text):
        """Extract answer and explanation from solution text"""
        if not solution_text:
            return None

        answer_info = {}

        # Try to find the correct answer (often mentioned in explanation)
        # This is a simplified approach - could be enhanced based on actual patterns
        if solution_text:
            answer_info["solution"] = solution_text.strip()

        return answer_info

    def extract_all_diagrams(self, container):
        """Extract all diagrams/images from container"""
        diagrams = []
        img_elements = container.css("img")

        for img in img_elements:
            img_src = img.css("::attr(src)").get()
            if img_src and not self.is_ad_image(img_src):
                diagrams.append(img_src)

        return diagrams

    def is_ad_image(self, img_src):
        """Check if an image is likely an advertisement"""
        if not img_src:
            return True

        # Educational images are usually in /qns/ directory
        if "/qns/" in img_src:
            return False

        # Other patterns that might indicate ads
        ad_patterns = ["banner", "ad", "sponsor", "promo"]
        return any(pattern in img_src.lower() for pattern in ad_patterns)

    def extract_theory_questions(self, response):
        """Extract theory questions using direct HTML parsing"""
        theory_questions = []

        # Find the theory questions section
        theory_section = response.css('h4.center:contains("THEORY QUESTIONS")')
        if not theory_section:
            return

        # Get the next div that contains all theory questions
        questions_container = theory_section[0].xpath("following-sibling::div[1]")[0]

        # Each theory question is in its own div
        question_divs = questions_container.css("div")

        for question_div in question_divs:
            # Skip advertisements
            if self.is_advertisement(question_div):
                continue

            # Parse the theory question
            question_data = self.parse_theory_question_improved(question_div)
            if question_data:
                theory_questions.append(question_data)

        # Sort by question number and remove duplicates
        theory_questions.sort(key=lambda x: x.get("number", 0))

        # Remove duplicates based on question number
        seen_numbers = set()
        unique_questions = []
        for question in theory_questions:
            if question["number"] not in seen_numbers:
                seen_numbers.add(question["number"])
                unique_questions.append(question)

        for question in unique_questions:
            yield question

    def parse_theory_question_improved(self, container):
        """Parse theory question with improved structure and answer integration"""
        full_text = self.extract_full_text(container)

        # Look for question number pattern
        num_match = re.search(r"(\d+)\.", full_text)
        if not num_match:
            return None

        question_num = int(num_match.group(1))

        # Split content into question part and solution part
        parts = re.split(r"\s+Show Solution\s+", full_text, 1)
        question_part = parts[0]
        solution_part = parts[1] if len(parts) > 1 else ""

        # Parse main question and subparts from question part
        main_question, subparts = self.parse_theory_structure_improved(
            question_part, question_num
        )

        # Parse solution and integrate with subparts
        if solution_part:
            subparts = self.integrate_theory_solutions(subparts, solution_part)

        # Extract all diagrams/images
        diagrams = self.extract_all_diagrams(container)

        if main_question or subparts:
            return {
                "section": "theory",
                "type": "theory",
                "number": question_num,
                "question": main_question,
                "subparts": subparts,
                "diagrams": diagrams if diagrams else [],
            }

        return None

    def parse_theory_structure_improved(self, question_part, question_num):
        """Parse theory question structure with better subpart handling"""
        # Remove question number
        content = re.sub(rf"^{question_num}\.?\s*", "", question_part)

        # Split by main parts (a), (b), (c), (d)
        main_parts = re.split(r"\s*\(([a-d])\)\s*", content)

        if len(main_parts) < 3:
            # No clear subparts, return as single question
            return content.strip(), []

        # First part might be main question text
        main_question = main_parts[0].strip()

        # Process subparts
        subparts = []
        for i in range(1, len(main_parts), 2):
            if i + 1 < len(main_parts):
                part_letter = main_parts[i]
                part_content = main_parts[i + 1].strip()

                # Parse sub-subparts within this part
                sub_subparts = self.parse_sub_subparts_improved(part_content)

                subpart_data = {
                    "part": f"({part_letter})",
                    "question": part_content if not sub_subparts else "",
                    "subparts": sub_subparts,
                }
                subparts.append(subpart_data)

        return main_question, subparts

    def parse_sub_subparts_improved(self, content):
        """Parse sub-subparts like (i), (ii) with better handling"""
        # Split by roman numerals or letters in parentheses
        sub_parts = re.split(r"\s*\(([ivx]+|[a-z])\)\s*", content)

        if len(sub_parts) < 3:
            return []

        sub_subparts = []
        for i in range(1, len(sub_parts), 2):
            if i + 1 < len(sub_parts):
                sub_letter = sub_parts[i]
                sub_content = sub_parts[i + 1].strip()

                if sub_content:
                    sub_subparts.append(
                        {"part": f"({sub_letter})", "question": sub_content}
                    )

        return sub_subparts

    def integrate_theory_solutions(self, subparts, solution_part):
        """Integrate solutions with corresponding subparts"""
        # This is a simplified approach - could be enhanced to match solutions to specific subparts
        for subpart in subparts:
            # Look for solutions that match this subpart
            part_letter = subpart["part"].strip("()")

            # Find solution for this part
            solution_pattern = rf"\({part_letter}\)(.*?)(?=\([a-d]\)|$)"
            solution_match = re.search(solution_pattern, solution_part, re.DOTALL)

            if solution_match:
                subpart["solution"] = solution_match.group(1).strip()

        return subparts

    def parse_theory_html_structure(self, question_div):
        """Parse theory question HTML structure into main question and subparts"""
        # Get all divs within the question
        all_divs = question_div.css("div")

        main_question = ""
        subparts = []
        current_part = None

        for div in all_divs:
            div_text = self.extract_full_text(div).strip()

            # Skip empty divs, question number, and solution sections
            if (
                not div_text
                or re.match(r"^\d+\.$", div_text)
                or "Show Solution" in div_text
            ):
                continue

            # Check if this is a main part (a), (b), (c), (d)
            main_part_match = re.match(r"^\(([a-d])\)", div_text)
            if main_part_match:
                # Save previous part if exists
                if current_part:
                    subparts.append(current_part)

                # Start new part
                part_letter = main_part_match.group(1)
                part_content = re.sub(r"^\([a-d]\)\s*", "", div_text)

                # Parse sub-subparts within this part
                sub_subparts = self.parse_sub_subparts_html(part_content)

                current_part = {
                    "part": f"({part_letter})",
                    "question": part_content if not sub_subparts else "",
                    "subparts": sub_subparts,
                }

            # Check if this is a sub-subpart (i), (ii), etc.
            elif re.match(r"^\(([ivx]+)\)", div_text):
                # This will be handled by parse_sub_subparts_html
                continue

            # If no parts found yet, this might be the main question
            elif not subparts and not current_part and not main_question:
                main_question = div_text

        # Add the last part
        if current_part:
            subparts.append(current_part)

        return main_question, subparts

    def parse_sub_subparts_html(self, content):
        """Parse sub-subparts like (i), (ii) from content"""
        # Split by roman numerals in parentheses
        parts = re.split(r"\s*\(([ivx]+)\)\s*", content)

        if len(parts) < 3:
            return []

        sub_subparts = []
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                sub_letter = parts[i]
                sub_content = parts[i + 1].strip()

                if sub_content:
                    sub_subparts.append(
                        {"part": f"({sub_letter})", "question": sub_content}
                    )

        return sub_subparts

    def parse_question_structure(self, content):
        """Parse question content into main question and structured subparts"""
        # Clean up content
        content = re.sub(r"\s+", " ", content).strip()

        # Split into parts by main sections (a), (b), (c), (d)
        main_parts = re.split(r"\s*\(([a-d])\)\s*", content)

        if len(main_parts) < 3:
            # No clear subparts structure, return as single question
            return content, []

        # First part is the main question (if any)
        main_question = main_parts[0].strip()

        # Process subparts
        subparts = []
        for i in range(1, len(main_parts), 2):
            if i + 1 < len(main_parts):
                part_letter = main_parts[i]
                part_content = main_parts[i + 1].strip()

                # Further split by sub-subparts (i), (ii), etc.
                sub_subparts = self.parse_sub_subparts(part_content)

                subpart_data = {
                    "part": f"({part_letter})",
                    "question": part_content if not sub_subparts else "",
                    "subparts": sub_subparts,
                }
                subparts.append(subpart_data)

        return main_question, subparts

    def parse_sub_subparts(self, content):
        """Parse sub-subparts like (i), (ii), (iii) within a main part"""
        # Split by roman numerals or letters in parentheses
        sub_parts = re.split(r"\s*\(([ivx]+|[a-z])\)\s*", content)

        if len(sub_parts) < 3:
            return []

        sub_subparts = []
        for i in range(1, len(sub_parts), 2):
            if i + 1 < len(sub_parts):
                sub_letter = sub_parts[i]
                sub_content = sub_parts[i + 1].strip()

                if sub_content:
                    sub_subparts.append(
                        {"part": f"({sub_letter})", "question": sub_content}
                    )

        return sub_subparts

    def extract_diagram(self, container):
        """Extract educational diagram URL from container"""
        img_elements = container.css("img")
        for img in img_elements:
            img_src = img.css("::attr(src)").get()
            if img_src and not self.is_ad_image(img_src):
                return img_src
        return None


# Configure settings in a standalone script
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    settings = get_project_settings()
    settings.update(
        {
            "FEEDS": {
                "bece_questions.json": {
                    "format": "json",
                    "overwrite": True,
                    "indent": 2,
                },
                "bece_questions.csv": {"format": "csv", "overwrite": True},
            },
            "LOG_LEVEL": "INFO",
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "DOWNLOAD_DELAY": 2,
        }
    )

    process = CrawlerProcess(settings)
    process.crawl(KuulchatSpider)
    process.start()

    # Verify output files
    if os.path.exists("bece_questions.json"):
        print("JSON file created: bece_questions.json")
    if os.path.exists("bece_questions.csv"):
        print("CSV file created: bece_questions.csv")
