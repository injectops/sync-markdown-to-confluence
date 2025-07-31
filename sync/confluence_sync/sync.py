from confluence_sync.remote_state import load_remote_state, save_remote_state
from confluence_sync import confluence_api as api


def run_sync():
    previous_state = load_remote_state()

    current_mapping = {}  # will be {md_file_path: confluence_page_id}
    current_files = find_markdown_files()  # your own logic that finds .md files

    # Handle deleted files
    deleted_files = set(previous_state.keys()) - set(current_files)
    for file_path in deleted_files:
        page_id = previous_state[file_path]
        api.delete_page(page_id)
        print(f"[INFO] Deleted removed page for: {file_path}")

    # Handle added or updated files
    for md_file in current_files:
        html_content = convert_md_to_confluence_html(md_file)  # your own function
        labels = parse_labels(md_file)                         # your own function
        page_title = resolve_title(md_file)                    # your own function
        parent_id = resolve_parent(md_file)                    # optional
        
        existing_page = api.get_page_by_title(page_title, config.SPACE_KEY)
        if existing_page:
            page_id = existing_page["id"]
            version = existing_page["version"]["number"]
            api.update_page(page_id, page_title, html_content, version)
        else:
            created = api.create_page(page_title, config.SPACE_KEY, html_content, parent_id)
            page_id = created["id"]
        
        api.add_labels(page_id, labels)
        current_mapping[md_file] = page_id

    # Save state to Confluence page
    save_remote_state(current_mapping)

if __name__ == "__main__":
    run_sync()
