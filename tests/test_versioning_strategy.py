import os

def needs_reindexing(file_path, previous_index):
    """
    Check if the given file needs to be reindexed.
    A file needs reindexing if it:
    - Is not present in the previous index
    - Has a newer modification time than previously recorded
    """
    try:
        last_indexed_mtime = previous_index.file_mtimes.get(file_path)
        current_mtime = os.path.getmtime(file_path)

        if last_indexed_mtime is None:
            return True
        return current_mtime > last_indexed_mtime
    except FileNotFoundError:
        # File was deleted or moved; optionally return False or True
        return True
