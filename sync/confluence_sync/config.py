import os

CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
EMAIL = os.getenv("EMAIL")
API_TOKEN = os.getenv("API_TOKEN")
SPACE_KEY = os.getenv("SPACE_KEY")
DEFAULT_PARENT_PAGE_ID = None
DOCS_DIR = os.getenv("DOCS_DIR", "docs")
