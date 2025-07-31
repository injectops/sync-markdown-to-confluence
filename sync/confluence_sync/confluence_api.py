import requests
import json
import os
from confluence_sync import config

BASE_URL = config.CONFLUENCE_BASE_URL
AUTH = (config.EMAIL, config.API_TOKEN)
HEADERS = {"Content-Type": "application/json"}


def get_page_by_title(title, space_key):
    """Return page object if found, else None."""
    url = f"{BASE_URL}/rest/api/content"
    params = {
        "title": title,
        "spaceKey": space_key,
        "expand": "body.storage,version",
    }
    res = requests.get(url, params=params, auth=AUTH, headers=HEADERS)
    data = res.json()
    return data["results"][0] if data.get("size", 0) > 0 else None
    

def create_page(title, space_key, html_body, parent_id=None):
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": html_body,
                "representation": "storage",
            }
        }
    }
    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]
    
    res = requests.post(f"{BASE_URL}/rest/api/content", headers=HEADERS, auth=AUTH, data=json.dumps(payload))
    res.raise_for_status()
    return res.json()


def delete_page(page_id):
    url = f"{BASE_URL}/rest/api/content/{page_id}"
    res = requests.delete(url, headers=HEADERS, auth=AUTH)
    res.raise_for_status()


def update_page(page_id, title, html_body, current_version):
    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": html_body,
                "representation": "storage",
            }
        }
    }
    
    res = requests.put(f"{BASE_URL}/rest/api/content/{page_id}", headers=HEADERS, auth=AUTH, data=json.dumps(payload))
    res.raise_for_status()
    return res.json()


def add_labels(page_id, labels):
    if not labels:
        return
    label_data = [{"prefix": "global", "name": label} for label in labels]
    url = f"{BASE_URL}/rest/api/content/{page_id}/label"
    res = requests.post(url, headers=HEADERS, auth=AUTH, data=json.dumps(label_data))
    res.raise_for_status()


def upload_attachment(page_id, file_path):
    #filename = file_path.split("/")[-1]
    filename = os.path.basename(file_path)
    url = f"{BASE_URL}/rest/api/content/{page_id}/child/attachment"

    # Check if the file exists
    params = {"filename": filename}
    existing = requests.get(url, params=params, auth=AUTH, headers=HEADERS).json()

    with open(file_path, 'rb') as f:
        files = {'file': (filename, f)}
        headers = {
            "X-Atlassian-Token": "no-check", # required for uploading attachments
        }

        if existing.get("size", 0) > 0:
            # Exists -> update it
            attachment_id = existing["results"][0]["id"]
            upload_url = f"{url}/{attachment_id}/data"
            res = requests.post(upload_url, headers=headers, auth=AUTH, files=files)
            res.raise_for_status()
        else:
            res = requests.post(url, headers=headers, auth=AUTH, files=files)
            res.raise_for_status()
