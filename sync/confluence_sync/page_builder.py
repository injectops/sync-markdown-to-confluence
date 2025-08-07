import os
from . import confluence_api, config, markdown_utils
from .attachments import upload_attachments_for_page


class PageBuilder:
    def __init__(self):
        self.page_cache = {}

    def _format_title(self, folder_name):
        return folder_name.replace("_", " ").strip()

    def ensure_page_hierarchy(self, folder_path_parts):
        """Create the folder hierarchy in Confluence, return parent page ID."""
        parent_id = config.DEFAULT_PARENT_PAGE_ID
        current_path = []

        for part in folder_path_parts:
            current_path.append(part)
            cache_key = "/".join(current_path)

            if cache_key in self.page_cache:
                parent_id = self.page_cache[cache_key]
                continue

            title = self._format_title(part)
            existing = confluence_api.get_page_by_title(title, config.SPACE_KEY)

            if existing:
                parent_id = existing["id"]
            else:
                created = confluence_api.create_page(title, config.SPACE_KEY, "<p>(placeholder)</p>", parent_id)
                parent_id = created["id"]

            self.page_cache[cache_key] = parent_id

        return parent_id

    def sync_page(self, folder_path, base_dir=config.DOCS_DIR):
        rel_path = os.path.relpath(folder_path, base_dir)
        folder_parts = rel_path.split(os.sep)

        frontmatter, html_content = markdown_utils.read_markdown_and_metadata(folder_path)

        title = frontmatter.get("title", self._format_title(folder_parts[-1]))
        labels = frontmatter.get("labels", [])

        parent_parts = folder_parts[:-1]
        parent_id = self.ensure_page_hierarchy(parent_parts) if parent_parts else config.DEFAULT_PARENT_PAGE_ID

        existing = confluence_api.get_page_by_title(title, config.SPACE_KEY)

        if existing:
            current_html = existing["body"]["storage"]["value"]
            if current_html == html_content.strip():
                print(f"Skipping {title} - no changes detected")
                page_id = existing["id"]
            else:
                updated = confluence_api.update_page(existing["id"], title, html_content, existing["version"]["number"])
                print(f"Updated {title}")
                page_id = updated["id"]
        else:
            created = confluence_api.create_page(title, config.SPACE_KEY, html_content, parent_id)
            print(f"Created {title}")
            page_id = created["id"]

        if labels:
            confluence_api.add_labels(page_id, labels)

        upload_attachments_for_page(folder_path, page_id)

        return page_id

page_builder = PageBuilder()
sync_page = page_builder.sync_page
