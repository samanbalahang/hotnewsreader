import os
import json
import time
from dotenv import load_dotenv

from utils.wordpress_api import WordPressAuth
from utils.file_manager import empty_news_folder, ensure_data_dirs
from utils.readrss import save_rss_as_json
from scrapers.news_spider import run_crawler

def main():
    load_dotenv()
    
    RSS_URL = os.getenv("RSS_FEED_URL")
    WP_URL = os.getenv("WORDPRESS_URL")
    WP_USER = os.getenv("WORDPRESS_USERNAME")
    WP_PWD = os.getenv("WORDPRESS_PASSWORD")
    
    MAX_LINKS = int(os.getenv("MAX_LINKS", 5))
    POST_DELAY = int(os.getenv("POST_DELAY", 60))

    DATA_JSON = "data/data.json"
    RAW_NEWS_DIR = "data/raw_news"

    print(f"--- 🚀 Starting Pipeline (Limit: {MAX_LINKS} articles) ---")

    ensure_data_dirs(['data', RAW_NEWS_DIR])
    empty_news_folder(RAW_NEWS_DIR)
    save_rss_as_json(RSS_URL, DATA_JSON)

    # 1. Load Registry
    try:
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ Error loading registry: {e}")
        return

    # 2. Filter items: ONLY those where uploaded is False
    items_to_process = [item for item in registry if not item.get('uploaded')][:MAX_LINKS]
    
    if not items_to_process:
        print("☕ No new articles to process. Everything is already uploaded.")
        return

    # 3. Scrape the selected items
    links_to_scrape = [item['link'] for item in items_to_process]
    print(f"🕸️ Scraping {len(links_to_scrape)} articles...")
    run_crawler(urls=links_to_scrape, folder=RAW_NEWS_DIR)

    # 4. WordPress Upload Loop
    wp = WordPressAuth(WP_URL)
    if wp.login(WP_USER, WP_PWD) is True:
        print("✅ Logged into WordPress.")

        # Map files to registry items using the link inside the file
        scraped_files = os.listdir(RAW_NEWS_DIR)
        
        for index, filename in enumerate(scraped_files):
            file_path = os.path.join(RAW_NEWS_DIR, filename)
            
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # The spider saves the URL on the first line
                source_url = lines[0].replace("SOURCE URL: ", "").strip()
                # The rest is the content
                content = "".join(lines[2:]) 

            # Find the matching item in our registry list to get its RSS title
            current_item = next((i for i in items_to_process if i['link'] == source_url), None)
            post_title = current_item['title'] if current_item else filename

            print(f"📝 [{index + 1}/{len(scraped_files)}] Uploading: {post_title}")
            
            # --- UPLOAD TO WORDPRESS ---
            result = wp.create_post(title=post_title, content=content, status='publish')

            if "id" in result:
                # SUCCESS: Mark this specific item as uploaded in the main registry
                for item in registry:
                    if item['link'] == source_url:
                        item['uploaded'] = True
                print(f"✅ Successfully posted to WP.")
            else:
                print(f"❌ Failed to upload {filename}. Keeping 'uploaded' as False.")

            # Apply Delay
            if index < len(scraped_files) - 1:
                print(f"⏳ Waiting {POST_DELAY} seconds...")
                time.sleep(POST_DELAY)

        # 5. Save the updated registry back to data.json
        with open(DATA_JSON, "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=4)
        print("💾 Registry updated with new upload statuses.")

        wp.logout()
    
    print("--- ✨ Pipeline Finished ---")

if __name__ == "__main__":
    main()