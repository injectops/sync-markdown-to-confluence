import json
import re
from confluence_sync import confluence_api as api, config

STATE_PAGE_TITLE = "Confluence Sync State"
SPACE_KEY = config.SPACE_KEY  # must be set in .env


def load_remote_state():
    """Fetch previous sync state (file path → page ID) from Confluence."""
    page = api.get_page_by_title(STATE_PAGE_TITLE, SPACE_KEY)
    if not page:
        print(f"[INFO] No state page '{STATE_PAGE_TITLE}' found.")
        return {}

    body = page["body"]["storage"]["value"]

    cleaned = re.sub(r"<\/?p>", "", body).strip()

    cleaned = cleaned.replace('&quot;', '"')

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[WARN] Failed to parse JSON from state page.")
        return {}


def save_remote_state(state_dict):
    """Save updated sync state to Confluence."""
    body = f"<p>{json.dumps(state_dict, indent=2)}</p>"
    existing = api.get_page_by_title(STATE_PAGE_TITLE, SPACE_KEY)

    if existing:
        api.update_page(existing["id"], STATE_PAGE_TITLE, body, existing["version"]["number"])
        print(f"[INFO] Updated state page '{STATE_PAGE_TITLE}'")
    else:
        api.create_page(STATE_PAGE_TITLE, SPACE_KEY, body)
        print(f"[INFO] Created state page '{STATE_PAGE_TITLE}'")
