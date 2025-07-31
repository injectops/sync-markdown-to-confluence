import os
from confluence_sync import config

def find_page_folders(base_dir=config.DOCS_DIR):
    page_folders = []
    for root, dirs, files in os.walk(base_dir):
        if 'README.md' in files:
            page_folders.append(root)
    return page_folders

