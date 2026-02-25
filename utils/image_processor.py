import requests
from PIL import Image
from io import BytesIO
import os

def download_and_resize_image(url, width, height, output_path="data/temp_image.jpg"):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Open image from bytes
        img = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary (e.g., converting PNG/WebP to JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Resize using Lanczos filter for high quality
        resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Save locally
        resized_img.save(output_path, "JPEG", quality=85)
        return output_path
    except Exception as e:
        print(f"⚠️ Image processing error: {e}")
        return None