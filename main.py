import os
import json
import time
from dotenv import load_dotenv
from utils.wordpress_api import WordPressAuth
from utils.file_manager import empty_news_folder, ensure_data_dirs
from utils.readrss import save_rss_as_json
from scrapers.news_spider import run_crawler
from utils.image_processor import download_and_resize_image
from urllib.parse import unquote
from utils.file_manager import all_json_uploaded

import re
def extract_id(url):
    """
    Extracts the numeric ID (5+ digits) from URLs.
    Handles: 
    - /12345-slug-text (Mid-URL ID)
    - /12345 (End-URL ID)
    """
    # 1. Clean the URL (remove trailing slashes and spaces)
    clean_url = url.strip('/ ')
    
    # 2. Look for 5 or more digits immediately after a slash
    # This is the most reliable for site: bartarinha.ir
    match = re.search(r'/(\d{5,})', clean_url)
    if match:
        return match.group(1)
    
    # 3. Fallback: Just find the last sequence of digits in the URL
    match_fallback = re.findall(r'(\d+)', clean_url)
    return match_fallback[-1] if match_fallback else url


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
    
    # Image settings from .env
    IMG_W = int(os.getenv("IMG_WIDTH", 800))
    IMG_H = int(os.getenv("IMG_HEIGHT", 600))

    # Initialize environment
    ensure_data_dirs(['data', RAW_NEWS_DIR])
    empty_news_folder(RAW_NEWS_DIR)
    if all_json_uploaded("data/data.json"):
        if os.path.exists("data/data.json"):
            os.remove("data/data.json")
            print("🗑️ data.json deleted.")
    
    # Update local registry with latest RSS entries
    save_rss_as_json(RSS_URL, DATA_JSON)

    # 1. Load Registry and Find TRULY new items
    try:
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            registry = json.load(f)
        
        items_to_process = []
        potential_items = [item for item in registry if not item.get('uploaded')]

        print(f"🔍 Scanning registry for {MAX_LINKS} new articles...")
        
        wp = WordPressAuth(WP_URL)
        if not wp.login(WP_USER, WP_PWD):
            print("❌ WordPress Login Failed. Check your .env credentials.")
            return

        for item in potential_items:
            if len(items_to_process) >= MAX_LINKS:
                break
            
            # Extract the numeric ID from the link
            article_id = extract_id(item['link'])
            existing_id = wp.post_exists_by_id(article_id)  # You would need to create this method in wordpress_api.py

            if existing_id:
                item['uploaded'] = True
                item['wp_id'] = existing_id
            else:
                items_to_process.append(item)

        # Save registry to remember duplicates found
        with open(DATA_JSON, "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=4)

        links_to_scrape = [item['link'] for item in items_to_process]
        
        if not links_to_scrape:
            print("☕ No new articles found. Everything is up to date.")
            wp.logout()
            time.sleep(60)  # wait a bit before restarting
            main()  # restart the whole process
            return
            
        print(f"📡 Scraping {len(links_to_scrape)} new articles...")
        run_crawler(urls=links_to_scrape, folder=RAW_NEWS_DIR)
        
    except Exception as e:
        print(f"❌ Selection/Crawler Error: {e}")
        return

    # 2. Process Scraped Files and Upload
    target_id = wp.get_category_id_by_slug(WP_CAT_SLUG)
    scraped_files = [f for f in os.listdir(RAW_NEWS_DIR) if f.endswith('.txt')]
    
    print(f"🚀 Found {len(scraped_files)} files in storage. Starting upload pipeline...")

    for index, filename in enumerate(scraped_files):
        file_path = os.path.join(RAW_NEWS_DIR, filename)
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) < 3:
                continue

            source_url = lines[0].replace("SOURCE URL: ", "").strip()
            img_url = lines[1].replace("IMAGE URL: ", "").strip()
            
            if len(lines) > 2 and "TITLE: " in lines[2]:
                post_title = lines[2].replace("TITLE: ", "").strip()
            else:
                post_title = os.path.splitext(filename)[0] 

            content = "".join(lines[4:]) 

        # --- Process Image ---
        feat_id = None
        if img_url and img_url != 'None':
            print(f"🖼️  Processing image for: {post_title[:40]}...")
            temp_img_path = "data/temp_featured.jpg"
            local_path = download_and_resize_image(img_url, IMG_W, IMG_H, temp_img_path)
            
            if local_path:
                feat_id = wp.upload_local_image(local_path)
                if os.path.exists(local_path):
                    os.remove(local_path)

        # --- Create WordPress Post ---
        print(f"📤 Posting to WordPress: {post_title[:40]}...")
        result = wp.create_post(
            title=post_title, 
            content=content, 
            categories=[target_id] if target_id else [], 
            featured_image_id=feat_id
        )
        
        # --- Capture WP_ID and Update Registry (STRICT MATCH) ---
        if isinstance(result, dict) and "id" in result:
            
            new_id = result["id"]
            clean_source_url = unquote(source_url.strip())
            source_id = extract_id(clean_source_url) # Get ID from scraped URL
            print(f"source_id : {source_id}")
            found_locally = False
            
            # Reload to prevent data loss
            with open(DATA_JSON, "r", encoding="utf-8") as f:
                registry = json.load(f)
            
            for item in registry:
                registry_item_id = extract_id(unquote(item['link'].strip())) # Get ID from JSON link
                if registry_item_id == source_id: # Compare IDs instead of full strings
                    item['uploaded'] = True
                    item['wp_id'] = new_id
                    found_locally = True
                    break
            
            with open(DATA_JSON, "w", encoding="utf-8") as f:
                json.dump(registry, f, ensure_ascii=False, indent=4)
            
            if found_locally:
                print(f"✅ Success! (WP ID: {new_id}) - Match by ID: {source_id}")
            else:
                print(f"⚠️ Posted, but ID {source_id} not found in JSON.")
        else:
            print(f"❌ Failed to post: {source_url}")
        
        if index < len(scraped_files) - 1:
            print(f"⏳ Waiting {POST_DELAY}s before next post...")
            time.sleep(POST_DELAY)
    
    wp.logout()
    print("\n--- ✨ Pipeline Finished ---")  
if __name__ == "__main__":
    main()