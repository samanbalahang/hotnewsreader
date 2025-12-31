import requests
from requests.auth import HTTPBasicAuth

class WordPressAuth:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.session = requests.Session()
        self.auth = None

    def login(self, username, password):
        try:
            self.auth = HTTPBasicAuth(username, password)
            response = self.session.get(f"{self.api_url}/users/me", auth=self.auth, timeout=10)
            return True if response.status_code == 200 else False
        except:
            return False

    def get_category_id_by_slug(self, slug):
        if not slug: return None
        try:
            response = self.session.get(f"{self.api_url}/categories", auth=self.auth, params={'slug': slug}, timeout=10)
            if response.status_code == 200 and len(response.json()) > 0:
                return response.json()[0]['id']
            return None
        except:
            return None

    def upload_image_from_url(self, image_url):
        """آپلود تصویر در وردپرس و دریافت ID"""
        if not image_url or image_url == 'None':
            return None
        try:
            img_res = requests.get(image_url, timeout=15)
            if img_res.status_code != 200: return None
            
            filename = image_url.split("/")[-1].split("?")[0] or "featured.jpg"
            headers = {
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'image/jpeg',
            }
            
            response = self.session.post(
                f"{self.api_url}/media",
                headers=headers,
                data=img_res.content,
                auth=self.auth,
                timeout=20
            )
            return response.json().get('id') if response.status_code == 201 else None
        except:
            return None

    def create_post(self, title, content, status='publish', categories=None, featured_image_id=None):
        if not self.auth: return {"error": "Not authenticated"}

        post_data = {
            'title': title,
            'content': content,
            'status': status,
        }
        if categories: post_data['categories'] = categories
        if featured_image_id: post_data['featured_media'] = featured_image_id

        try:
            response = self.session.post(f"{self.api_url}/posts", auth=self.auth, json=post_data, timeout=15)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def logout(self):
        self.session.close()
        return True