import os

def get_hybrid_mode_strategy(file_path):
    """
    Determine blame strategy based on file characteristics.

    Strategy Rules:
    - Use 'eager' for frequently queried core/API files
    - Use 'lazy' for tests and utility tools
    - Fallback: use 'eager' for small files, 'lazy' for large ones (100KB threshold)
    """
    try:
        if file_path.startswith(('src/core/', 'src/api/')):
            return 'eager'
        elif file_path.startswith(('tests/', 'tools/')):
            return 'lazy'

        file_size = os.path.getsize(file_path)
        return 'eager' if file_size < 100 * 1024 else 'lazy'

    except (FileNotFoundError, OSError):
        # If file doesn't exist or can't be accessed, default to 'lazy'
        return 'lazy'
