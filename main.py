import scrapy
import re
import os

class KuulchatSpider(scrapy.Spider):
    name = 'kuulchat'
    start_urls = ['https://kuulchat.com/bece/questions/science-2022/']

    def parse(self, response):
        # Extract objective questions
        for sel in response.css('div.inner h4.center:contains("OBJECTIVE TEST") ~ div[style*="margin-bottom:10px"]'):
            num = sel.css('span.bold::text').get(default='').strip()
            num = int(re.search(r'\d+', num).group()) if re.search(r'\d+', num) else 0
            stem = sel.css('div[style*="width:93%"] p::text').get(default='').strip()
            options = sel.css('div[style*="width:75%"] p::text').getall()[:4]
            diagram = sel.css('img::attr(src)').get(default=None)

            yield {
                'section': 'objective',
                'type': 'mcq',
                'number': num,
                'question': stem,
                'options': {
                    'A': options[0].strip() if len(options) > 0 else '',
                    'B': options[1].strip() if len(options) > 1 else '',
                    'C': options[2].strip() if len(options) > 2 else '',
                    'D': options[3].strip() if len(options) > 3 else ''
                },
                'diagram': diagram
            }

        # Extract theory questions
        theory_section = response.css('h4.center:contains("THEORY QUESTIONS") ~ *')
        current_question = None
        current_num = 0
        subparts = []

        for sel in theory_section.css('div, p, li'):
            text = ' '.join(sel.css('::text').getall()).strip()
            if not text or 'THEORY QUESTIONS' in text:
                continue

            num_match = sel.css('span.bold::text, .num::text').get(default='').strip()
            num = int(re.search(r'\d+', num_match).group()) if re.search(r'\d+', num_match) else 0
            subpart_match = re.match(r'^\([a-z]\)|^\([ivx]+\)', text, re.IGNORECASE)
            diagram = sel.css('img::attr(src)').get(default=None)

            if num and num != current_num:
                if current_question:
                    yield {
                        'section': 'theory',
                        'type': 'theory',
                        'number': current_num,
                        'question': current_question,
                        'subparts': subparts,
                        'diagram': diagram
                    }
                current_question = text
                current_num = num
                subparts = []
            elif subpart_match:
                subpart_key = subpart_match.group()
                subpart_text = text[len(subpart_key):].strip()
                subparts.append({subpart_key: subpart_text})
            else:
                current_question = (current_question or '') + ' ' + text

        if current_question:
            yield {
                'section': 'theory',
                'type': 'theory',
                'number': current_num,
                'question': current_question.strip(),
                'subparts': subparts,
                'diagram': diagram
            }

        # Handle pagination
        next_page = response.css('a.next::attr(href), .pagination a:contains("Next")::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

# Configure settings in a standalone script
if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    settings = get_project_settings()
    settings.update({
        'FEEDS': {
            'bece_questions.json': {'format': 'json', 'overwrite': True, 'indent': 2},
            'bece_questions.csv': {'format': 'csv', 'overwrite': True},
        },
        'LOG_LEVEL': 'INFO',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 2,
    })

    process = CrawlerProcess(settings)
    process.crawl(KuulchatSpider)
    process.start()

    # Verify output files
    if os.path.exists('bece_questions.json'):
        print("JSON file created: bece_questions.json")
    if os.path.exists('bece_questions.csv'):
        print("CSV file created: bece_questions.csv")