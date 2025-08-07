import requests
import json
import os
from . import config

class ConfluenceAPI:
    STATE_PAGE_TITLE = "Confluence Sync State"
    STATE_ATTACHMENT_NAME = "state.json"

    def __init__(self):
        self.base_url = config.CONFLUENCE_BASE_URL
        self.space_key = config.SPACE_KEY
        self.session = requests.Session()
        self.session.auth = (config.EMAIL, config.API_TOKEN)
        self.session.headers.update({"Content-Type": "application/json"})

    def _request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def get_page_by_title(self, title, space_key):
        """Return page object if found, else None."""
        url = f"{self.base_url}/rest/api/content"
        params = {
            "title": title,
            "spaceKey": space_key,
            "expand": "body.storage,version",
        }
        res = self._request("GET", url, params=params)
        data = res.json()
        return data["results"][0] if data.get("size", 0) > 0 else None

    def create_page(self, title, space_key, html_body, parent_id=None):
        url = f"{self.base_url}/rest/api/content"
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

        res = self._request("POST", url, data=json.dumps(payload))
        return res.json()

    def delete_page(self, page_id):
        url = f"{self.base_url}/rest/api/content/{page_id}"
        self._request("DELETE", url)

    def update_page(self, page_id, title, html_body, current_version):
        url = f"{self.base_url}/rest/api/content/{page_id}"
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

        res = self._request("PUT", url, data=json.dumps(payload))
        return res.json()

    def add_labels(self, page_id, labels):
        if not labels:
            return
        url = f"{self.base_url}/rest/api/content/{page_id}/label"
        label_data = [{"prefix": "global", "name": label} for label in labels]
        self._request("POST", url, data=json.dumps(label_data))

    def get_attachment(self, page_id, filename):
        url = f"{self.base_url}/rest/api/content/{page_id}/child/attachment"
        params = {"filename": filename}
        res = self._request("GET", url, params=params)
        data = res.json()
        return data["results"][0] if data.get("size", 0) > 0 else None

    def upload_attachment(self, page_id, file_path, filename=None):
        filename = filename or os.path.basename(file_path)
        url = f"{self.base_url}/rest/api/content/{page_id}/child/attachment"

        existing = self.get_attachment(page_id, filename)

        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            headers = {"X-Atlassian-Token": "no-check"}

            if existing:
                attachment_id = existing["id"]
                upload_url = f"{url}/{attachment_id}/data"
                self._request("POST", upload_url, headers=headers, files=files)
            else:
                self._request("POST", url, headers=headers, files=files)

    def load_remote_state(self):
        """Fetch previous sync state (file path → page ID) from Confluence."""
        state_page = self.get_page_by_title(self.STATE_PAGE_TITLE, self.space_key)
        if not state_page:
            print(f"[INFO] No state page '{self.STATE_PAGE_TITLE}' found.")
            return {}

        attachment = self.get_attachment(state_page["id"], self.STATE_ATTACHMENT_NAME)
        if not attachment:
            print(f"[INFO] No state attachment '{self.STATE_ATTACHMENT_NAME}' found.")
            return {}

        download_url = self.base_url + attachment["_links"]["download"]
        res = self._request("GET", download_url)

        try:
            return res.json()
        except json.JSONDecodeError:
            print(f"[WARN] Failed to parse JSON from state attachment.")
            return {}

    def save_remote_state(self, state_dict):
        """Save updated sync state to Confluence."""
        state_page = self.get_page_by_title(self.STATE_PAGE_TITLE, self.space_key)
        if not state_page:
            state_page = self.create_page(self.STATE_PAGE_TITLE, self.space_key, "<p>This page stores the sync state.</p>")
            print(f"[INFO] Created state page '{self.STATE_PAGE_TITLE}'")

        state_file = "remote-state.json"
        with open(state_file, "w") as f:
            json.dump(state_dict, f, indent=2)

        self.upload_attachment(state_page["id"], state_file, filename=self.STATE_ATTACHMENT_NAME)
        print(f"[INFO] Updated state attachment '{self.STATE_ATTACHMENT_NAME}'")
        os.remove(state_file)
