from confluence_sync import file_walker, page_builder, config, remote_state, confluence_api

def main():
    print("Scanning for page pages...")
    page_folders = file_walker.find_page_folders(config.DOCS_DIR)
    previous_state = remote_state.load_remote_state()
    current_state = {}


    for folder in sorted(page_folders):
        print(f"Processing folder: {folder}")
        try:
            page_builder.sync_page(folder)
            page_id = page_builder.sync_page(folder)
            current_state[folder] = page_id
        except Exception as e:
            print(f"Error processing {folder}: {e}")

    deleted_folders = set(previous_state.keys()) - set(current_state.keys())
    
    for folder in deleted_folders:
        page_id = previous_state[folder]
        try:
            confluence_api.delete_page(page_id)
            print(f"Deleted page for removed folder: {folder}")
        except Exception as e:
            print(f"Failed to delete page for {folder}: {e}")

    remote_state.save_remote_state(current_state)
    print("Sync complete.")

if __name__ == "__main__":
    main()

