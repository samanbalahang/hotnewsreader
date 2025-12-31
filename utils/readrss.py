import json
import feedparser
import os
from dotenv import load_dotenv

def save_rss_as_json(url, filename="data/data.json"):
    """
    Parses the RSS feed, adds an 'uploaded' flag, and merges 
    new entries into the existing JSON registry.
    """
    # 1. Ensure the directory for the filename exists (e.g., the 'data' folder)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # 2. Parse the RSS feed
    print(f"📡 Fetching RSS feed from: {url}")
    feed = feedparser.parse(url)
    
    if not feed.entries:
        print("⚠️ No entries found in the RSS feed. Check the URL or your connection.")
        return

    # Create a list of the new entries from the feed
    new_entries = [
        {
            "title": e.title, 
            "link": e.link, 
            "uploaded": False 
        } 
        for e in feed.entries
    ]
    
    # 3. Load existing data if file exists to prevent duplicates
    existing_data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            print(f"⚠️ {filename} was corrupted or empty. Starting fresh.")
            existing_data = []

    # 4. Merge data (Avoid Duplicates based on the 'link')
    existing_links = {item['link'] for item in existing_data}
    
    added_count = 0
    for entry in new_entries:
        if entry['link'] not in existing_links:
            existing_data.append(entry)
            added_count += 1

    # 5. Save the updated list back to the JSON file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Processed {len(new_entries)} entries. Added {added_count} new links to registry.")
    except Exception as e:
        print(f"❌ Failed to save JSON: {e}")

if __name__ == "__main__":
    # This block runs ONLY if you execute this file directly
    load_dotenv() # Load variables from .env
    rss_url = os.getenv("RSS_FEED_URL")
    
    if rss_url:
        print("Running standalone test with URL from .env...")
        save_rss_as_json(rss_url, "data/data.json")
    else:
        print("❌ Error: RSS_FEED_URL not found in .env file.")