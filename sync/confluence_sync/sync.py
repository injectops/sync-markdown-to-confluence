from . import file_walker, config
from .confluence_api import ConfluenceAPI
from .page_builder import PageBuilder

def run_sync():
    """
    Orchestrates the synchronization process between the local documentation
    directory and a Confluence space.
    """
    # Composition Root: Create and wire up dependencies
    api_client = ConfluenceAPI()
    page_builder = PageBuilder(api_client)

    print("Scanning for page pages...")
    page_folders = file_walker.find_page_folders(config.DOCS_DIR)
    previous_state = api_client.load_remote_state()
    current_state = {}

    for folder in sorted(page_folders):
        print(f"Processing folder: {folder}")
        try:
            page_id = page_builder.sync_page(folder)
            if page_id:
                current_state[folder] = page_id
        except Exception as e:
            print(f"Error processing {folder}: {e}")

    deleted_folders = set(previous_state.keys()) - set(current_state.keys())

    for folder in deleted_folders:
        page_id = previous_state[folder]
        try:
            api_client.delete_page(page_id)
            print(f"Deleted page for removed folder: {folder}")
        except Exception as e:
            print(f"Failed to delete page for {folder}: {e}")

    api_client.save_remote_state(current_state)
    print("Sync complete.")
