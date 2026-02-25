import json
import feedparser
import os
import re
from dotenv import load_dotenv

def clean_persian(text):
    """
    Standardizes Persian characters to ensure matches work correctly.
    Replaces Arabic variants of 'K' and 'Y' with Persian ones.
    """
    if not text:
        return ""
    # Standardizing characters: 
    # Arabic Yeh \u064a -> Persian Yeh \u06cc
    # Arabic Keheh \u0643 -> Persian Keheh \u06a9
    return text.replace('ي', 'ی').replace('ك', 'ک').strip()

def save_rss_as_json(url, filename="data/data.json"):
    """
    Parses the RSS feed, extracts numeric IDs, adds an 'uploaded' flag, 
    and merges new entries into the existing JSON registry.
    """
    # 1. Ensure the directory for the filename exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # 2. Parse the RSS feed
    print(f"📡 Fetching RSS feed from: {url}")
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"❌ Error parsing RSS feed: {e}")
        return
    
    if not feed.entries:
        print("⚠️ No entries found in the RSS feed. Check the URL or connection.")
        return

    # 3. Load existing data if file exists
    existing_data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            print(f"⚠️ {filename} was corrupted. Starting fresh.")
            existing_data = []

    # 4. Merge data (Avoid Duplicates)
    added_count = 0
    
    # Create sets for efficient duplicate checking
    existing_links = {item['link'].strip() for item in existing_data}
    existing_titles = {clean_persian(item['title']) for item in existing_data}

    # Process entries (reversed to keep chronological order)
    for entry in reversed(feed.entries):
        new_title = entry.title.strip()
        new_link = entry.link.strip()
        cleaned_new_title = clean_persian(new_title)

        # --- NEW EDIT: EXTRACT ID ---
        # Look for the numeric ID (6 or more digits) in the RSS link
        match = re.search(r'(\d{6,})', new_link)
        article_id = match.group(1) if match else None

        # Check if this item is truly new
        if new_link not in existing_links and cleaned_new_title not in existing_titles:
            existing_data.append({
                "article_id": article_id,  # <--- Saved here for main.py to use
                "title": new_title, 
                "link": new_link, 
                "uploaded": False 
            })
            # Update lookup sets
            existing_links.add(new_link)
            existing_titles.add(cleaned_new_title)
            added_count += 1

    # 5. Cleanup (Rolling Window)
    MAX_REGISTRY_SIZE = 200 
    if len(existing_data) > MAX_REGISTRY_SIZE:
        existing_data = existing_data[-MAX_REGISTRY_SIZE:]
        print(f"🧹 Registry trimmed to latest {MAX_REGISTRY_SIZE} items.")

    # 6. Save with Persian character support
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"✅ RSS Updated. Added {added_count} items. Total: {len(existing_data)}")
    except Exception as e:
        print(f"❌ Failed to save JSON: {e}")

if __name__ == "__main__":
    load_dotenv()
    rss_url = os.getenv("RSS_FEED_URL")
    if rss_url:
        save_rss_as_json(rss_url, "data/data.json")