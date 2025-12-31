import os
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import unquote
import ssl

# Handle SSL issues for specific news sites
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

class NewsSpider(scrapy.Spider):
    name = 'news_spider'
    
    def __init__(self, urls=None, folder='data/raw_news', *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        # These URLs are now passed exclusively from main.py
        self.start_urls = urls if urls else []
        self.folder = folder
        
        # Ensure the output directory exists
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def parse(self, response):
        """
        Main parsing method with robust error handling to prevent 
        individual page failures from stopping the crawl.
        """
        try:
            # 1. Generate a safe filename
            decoded_url = unquote(response.url)
            raw_filename = decoded_url.rstrip('/').split("/")[-1] or "index"
            
            safe_filename = "".join([c for c in raw_filename if c.isalnum() or c in (' ', '.', '_')]).rstrip()
            if not safe_filename.endswith(".txt"):
                safe_filename += ".txt"
            
            file_path = os.path.join(self.folder, safe_filename)

            # 2. Content Extraction
            # Broad selectors to catch content from various news CMS types
            content_selector = (
                '.body.row h1, .body.row h2, .body.row p, '
                '.itemBody h1, .itemBody p, '
                'article h1, article p, .entry-content p'
            )
            
            content_elements = response.css(content_selector).getall()
            
            clean_text = []
            for html_snippet in content_elements:
                # Use a nested try-except for element-level parsing
                try:
                    text = scrapy.Selector(text=html_snippet).xpath('//text()').get()
                    if text and text.strip():
                        clean_text.append(text.strip())
                except Exception as e:
                    self.logger.warning(f"Failed to parse a text block on {response.url}: {e}")

            # 3. Save to File
            if clean_text:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"SOURCE URL: {response.url}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write("\n\n".join(clean_text))
                self.log(f'✅ Saved: {safe_filename}')
            else:
                self.log(f'⚠️ No content found: {response.url}')

        except Exception as e:
            # Catch-all for any unexpected errors during the parsing of a single page
            self.logger.error(f"❌ Critical error parsing {response.url}: {e}")

def run_crawler(urls, folder):
    """
    Final entry point for main.py to trigger the spider.
    """
    if not urls:
        print("⚠️ No URLs to crawl. Skipping scraper.")
        return

    settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': False, 
        'DOWNLOAD_DELAY': 1,      
    }

    process = CrawlerProcess(settings)
    process.crawl(NewsSpider, urls=urls, folder=folder)
    process.start()

# Note: Test block removed. Run via main.py to use actual data.json links.