import os
from . import confluence_api

def upload_attachments_for_page(folder_path, page_id):
    attachments_dir = os.path.join(folder_path, "attachments")

    if not os.path.isdir(attachments_dir):
        return

    if not os.listdir(attachments_dir):
        return

    for file in os.listdir(attachments_dir):
        file_path = os.path.join(attachments_dir, file)
        
        if os.path.isfile(file_path):
            try:
                confluence_api.upload_attachment(page_id, file_path)
                print(f"Uploaded attachment: {file} to page ID: {page_id}")
            except Exception as e:
                print(f"Failed to upload {file}: {e}")
