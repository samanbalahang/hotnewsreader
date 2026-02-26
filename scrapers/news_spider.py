import os
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import unquote
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

class NewsSpider(scrapy.Spider):
    name = 'news_spider'
    
    def __init__(self, urls=None, folder='data/raw_news', *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls if urls else []
        self.folder = folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def parse(self, response):
            try:
                # 1. Get the actual page title
                page_title = response.css('title::text').get() or "no_title"
                page_title = page_title.strip()

                # 2. Filename cleanup (keep it for the file system)
                forbidden_chars = r'\/:*?"<>|'
                safe_filename = "".join([c for c in page_title if c not in forbidden_chars])
                safe_filename = safe_filename[:150]
                if not safe_filename.endswith(".txt"):
                    safe_filename += ".txt"
                
                file_path = os.path.join(self.folder, safe_filename)

                # 3. Extract Image
                image_url = response.css('meta[property="og:image"]::attr(content)').get()
                if not image_url:
                    image_url = response.css('article img::attr(src), .entry-content img::attr(src), img::attr(src)').get()

                # 4. Extract Content
                content_selector = (
                    '.primary_inf h1,.primary_inf h2,.primary_inf h3, '
                    '.primary_inf h4,.primary_inf h5,.primary_inf h6,.primary_inf p ,.primary_inf span ,.primary_inf li ,.primary_inf b,.primary_inf strong ,.primary_inf i ,.primary_inf em,'
                    'article h1, article p, .entry-content p,.right_newsinfo'
                    'main *:not(a),'
                )
                content_elements = response.css(content_selector).getall()
                
                clean_text = []
                for html_snippet in content_elements:
                    text = scrapy.Selector(text=html_snippet).xpath('//text()').get()
                    if text and text.strip():
                        clean_text.append(text.strip())

                # 5. SAVE TO FILE (Added TITLE line)
                if clean_text:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"SOURCE URL: {response.url}\n")
                        f.write(f"IMAGE URL: {image_url if image_url else 'None'}\n")
                        f.write(f"TITLE: {page_title}\n")  # <--- NEW LINE: Explicit Title
                        f.write("=" * 50 + "\n\n")
                        f.write("\n\n".join(clean_text))
                    self.log(f'✅ Saved: {safe_filename}')
                else:
                    self.log(f'⚠️ No content: {response.url}')

            except Exception as e:
                self.logger.error(f"❌ Error: {e}")

def run_crawler(urls, folder):
    if not urls:
        print("⚠️ No URLs to crawl.")
        return

    settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': False, 
        'DOWNLOAD_DELAY': 1,      
    }

    process = CrawlerProcess(settings)
    process.crawl(NewsSpider, urls=urls, folder=folder)
    process.start()