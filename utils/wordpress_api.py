import requests
from requests.auth import HTTPBasicAuth

class WordPressAuth:
    def __init__(self, base_url):
        """Initialize with the WordPress site URL."""
        # Ensure the URL doesn't have a trailing slash for consistency
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.session = requests.Session()
        self.auth = None

    def login(self, username, password):
        """
        Authenticate using Application Passwords via HTTP Basic Auth.
        WordPress treats Application Passwords as a form of Basic Auth.
        """
        try:
            # Set up the auth object
            self.auth = HTTPBasicAuth(username, password)
            
            # Verify credentials by hitting the 'users/me' endpoint
            # We use the session to benefit from connection pooling
            response = self.session.get(
                f"{self.api_url}/users/me",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                self.auth = None
                error_msg = response.json().get('message', 'Unknown error')
                return f"Authentication failed: {error_msg}"
        
        except requests.exceptions.RequestException as e:
            self.auth = None
            return f"Connection error: {str(e)}"

    def is_authenticated(self):
        """Check if the current session/auth is valid."""
        if not self.auth:
            return False
        
        try:
            response = self.session.get(f"{self.api_url}/users/me", auth=self.auth, timeout=10)
            return response.status_code == 200
        except:
            return False

    def get_current_user(self):
        """Return current user data if authenticated."""
        if not self.auth:
            return {"error": "Not authenticated"}

        try:
            response = self.session.get(f"{self.api_url}/users/me", auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def logout(self):
        """Clear authentication credentials and close the session."""
        self.auth = None
        self.session.close()
        print("🔒 WordPress session closed.")
        return True