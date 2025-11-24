import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

WP_BASE_URL = os.getenv("WP_BASE_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_DEFAULT_STATUS = os.getenv("WP_DEFAULT_STATUS", "draft")

class WordPressError(Exception):
    pass

def _get_auth_header():
    token = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

def publish_post(title: str, content: str, status: str = None):
    if status is None:
        status = WP_DEFAULT_STATUS

    endpoint = WP_BASE_URL.rstrip("/") + "/wp-json/wp/v2/posts"
    resp = requests.post(endpoint, headers=_get_auth_header(), json={
        "title": title,
        "content": content,
        "status": status,
    }, timeout=20)

    if resp.status_code not in (200, 201):
        raise WordPressError(resp.text)

    return resp.json()
