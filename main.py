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
        # Extract objective questions - improved selectors
        objective_section = response.css('h4.center:contains("OBJECTIVE TEST")')
        if not objective_section:
            return

        # Find all question containers after the OBJECTIVE TEST header
        question_containers = response.css('h4.center:contains("OBJECTIVE TEST") ~ div')

        for container in question_containers:
            # Skip if this is an advertisement
            if self.is_advertisement(container):
                continue

            # Stop if we've reached the theory section
            if container.css('h4.center:contains("THEORY QUESTIONS")'):
                break

            # Look for question number
            num_element = container.css("span.bold, .num")
            if not num_element:
                continue

            num_text = self.extract_full_text(num_element[0])
            num_match = re.search(r"(\d+)", num_text)
            if not num_match:
                continue

            question_num = int(num_match.group(1))

            # Extract question text - look for the main question content
            question_text = ""
            question_elements = container.css("p, div")
            for elem in question_elements:
                elem_text = self.extract_full_text(elem)
                # Skip if it's just the number or empty
                if re.match(r"^\d+\.$", elem_text.strip()) or not elem_text.strip():
                    continue
                # Skip if it looks like an option (starts with A., B., etc.)
                if re.match(r"^[A-E]\.\s", elem_text.strip()):
                    break
                # This looks like question text
                if elem_text and not question_text:
                    question_text = elem_text
                    break

            # Extract options
            options = {"A": "", "B": "", "C": "", "D": ""}
            option_elements = container.css(
                'div[style*="width:75%"] p, div:contains("A."), div:contains("B."), div:contains("C."), div:contains("D.")'
            )

            for elem in option_elements:
                elem_text = self.extract_full_text(elem)
                # Match option pattern
                option_match = re.match(r"^([A-E])\.\s*(.+)", elem_text.strip())
                if option_match:
                    option_letter = option_match.group(1)
                    option_text = option_match.group(2)
                    if option_letter in options:
                        options[option_letter] = option_text

            # Extract diagram URL (filter out ads)
            diagram = None
            img_elements = container.css("img")
            for img in img_elements:
                img_src = img.css("::attr(src)").get()
                if img_src and not self.is_ad_image(img_src):
                    diagram = img_src
                    break

            # Only yield if we have meaningful content
            if question_text and question_num > 0:
                yield {
                    "section": "objective",
                    "type": "mcq",
                    "number": question_num,
                    "question": question_text,
                    "options": options,
                    "diagram": diagram,
                }

        # Extract theory questions
        yield from self.extract_theory_questions(response)

        # Handle pagination
        next_page = response.css(
            'a.next::attr(href), .pagination a:contains("Next")::attr(href)'
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

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
        """Extract theory questions with improved parsing"""
        # Find the theory section
        theory_header = response.css('h4.center:contains("THEORY QUESTIONS")')
        if not theory_header:
            return

        # Get all content after the theory header until the end
        theory_containers = response.css('h4.center:contains("THEORY QUESTIONS") ~ div')

        current_question = None
        current_num = 0
        current_subparts = []
        current_diagram = None

        for container in theory_containers:
            # Skip advertisements
            if self.is_advertisement(container):
                continue

            # Look for main question numbers (1., 2., 3., etc.)
            question_num_match = self.extract_question_number(container)

            if question_num_match and question_num_match != current_num:
                # Yield previous question if exists
                if current_question and current_num > 0:
                    yield {
                        "section": "theory",
                        "type": "theory",
                        "number": current_num,
                        "question": current_question,
                        "subparts": current_subparts,
                        "diagram": current_diagram,
                    }

                # Start new question
                current_num = question_num_match
                current_question = self.extract_question_text(container)
                current_subparts = []
                current_diagram = self.extract_diagram(container)

            elif current_num > 0:  # We're in a question
                # Look for subparts (a), (b), (i), (ii), etc.
                subparts = self.extract_subparts(container)
                current_subparts.extend(subparts)

                # Update diagram if found
                diagram = self.extract_diagram(container)
                if diagram:
                    current_diagram = diagram

        # Yield the last question
        if current_question and current_num > 0:
            yield {
                "section": "theory",
                "type": "theory",
                "number": current_num,
                "question": current_question,
                "subparts": current_subparts,
                "diagram": current_diagram,
            }

    def extract_question_number(self, container):
        """Extract main question number from container"""
        # Look for patterns like "1.", "2.", etc.
        text = self.extract_full_text(container)
        match = re.search(r"^(\d+)\.", text.strip())
        return int(match.group(1)) if match else None

    def extract_question_text(self, container):
        """Extract the main question text"""
        text = self.extract_full_text(container)
        # Remove the question number prefix
        text = re.sub(r"^\d+\.\s*", "", text)
        return text.strip()

    def extract_subparts(self, container):
        """Extract subparts like (a), (b), (i), (ii) from container"""
        subparts = []
        text = self.extract_full_text(container)

        # Look for subpart patterns
        subpart_patterns = [
            r"\(([a-z])\)\s*(.+?)(?=\([a-z]\)|$)",  # (a), (b), etc.
            r"\(([ivx]+)\)\s*(.+?)(?=\([ivx]+\)|$)",  # (i), (ii), (iii), etc.
        ]

        for pattern in subpart_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                subpart_key = f"({match.group(1)})"
                subpart_text = match.group(2).strip()
                if subpart_text:
                    subparts.append({subpart_key: subpart_text})

        return subparts

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
