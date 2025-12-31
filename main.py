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
    WP_CAT_SLUG = os.getenv("WP_CATEGORY_SLUG")
    MAX_LINKS = int(os.getenv("MAX_LINKS", 5))
    POST_DELAY = int(os.getenv("POST_DELAY", 60))
    DATA_JSON = "data/data.json"
    RAW_NEWS_DIR = "data/raw_news"

    ensure_data_dirs(['data', RAW_NEWS_DIR])
    empty_news_folder(RAW_NEWS_DIR)
    save_rss_as_json(RSS_URL, DATA_JSON)

    try:
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            registry = json.load(f)
        new_items = [item for item in registry if not item.get('uploaded')]
        items_to_process = new_items[:MAX_LINKS]
        links_to_scrape = [item['link'] for item in items_to_process]
        
        if not links_to_scrape:
            print("☕ No new articles.")
            return
            
        run_crawler(urls=links_to_scrape, folder=RAW_NEWS_DIR)
    except Exception as e:
        print(f"❌ Registry Error: {e}")
        return

    wp = WordPressAuth(WP_URL)
    if wp.login(WP_USER, WP_PWD):
        target_id = wp.get_category_id_by_slug(WP_CAT_SLUG)
        scraped_files = [f for f in os.listdir(RAW_NEWS_DIR) if f.endswith('.txt')]
        
        for index, filename in enumerate(scraped_files):
            file_path = os.path.join(RAW_NEWS_DIR, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                source_url = lines[0].replace("SOURCE URL: ", "").strip()
                img_url = lines[1].replace("IMAGE URL: ", "").strip()
                content = "".join(lines[3:]) # متن بعد از خط جداکننده

            current_item = next((i for i in items_to_process if i['link'] == source_url), None)
            post_title = current_item['title'] if current_item else filename

            # آپلود تصویر شاخص
            feat_id = None
            if img_url and img_url != 'None':
                print(f"🖼️ Uploading image for: {post_title[:30]}...")
                feat_id = wp.upload_image_from_url(img_url)

            # ارسال پست
            result = wp.create_post(post_title, content, categories=[target_id] if target_id else [], featured_image_id=feat_id)
            
            if isinstance(result, dict) and "id" in result:
                for item in registry:
                    if item['link'] == source_url: item['uploaded'] = True
                print(f"✅ Posted successfully.")
            
            with open(DATA_JSON, "w", encoding="utf-8") as f:
                json.dump(registry, f, ensure_ascii=False, indent=4)

            if index < len(scraped_files) - 1:
                time.sleep(POST_DELAY)
        wp.logout()
    print("--- ✨ Pipeline Finished ---")

if __name__ == "__main__":
    main()