import os
import pathlib
from typing import List, Set, Optional, Iterator

class FileCrawler:
    """Recursively scans directories for Python source files with configurable exclusions."""
    
    def __init__(
        self,
        follow_symlinks: bool = False,
        excluded_dirs: Optional[Set[str]] = None,
        max_file_size_mb: int = 10
    ):
        # Default directories to exclude
        self.excluded_dirs = {
            ".venv", "venv", "__pycache__", ".git", 
            "node_modules", ".tox", ".eggs", "build", "dist"
        }
        
        # Add user-specified exclusions
        if excluded_dirs:
            self.excluded_dirs.update(excluded_dirs)
            
        self.follow_symlinks = follow_symlinks
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
    
    def scan_directory(self, root_path: str) -> List[pathlib.Path]:
        """
        Scan directory recursively for Python files.
        
        Args:
            root_path: Directory to scan
            
        Returns:
            List of normalized paths to valid Python files
        """
        root = pathlib.Path(root_path).resolve()
        
        if not root.exists():
            raise FileNotFoundError(f"Path does not exist: {root}")
            
        if not root.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {root}")
            
        return list(self._scan_recursive(root))
    
    def _scan_recursive(self, directory: pathlib.Path) -> Iterator[pathlib.Path]:
        """Yield valid Python files from directory and subdirectories."""
        try:
            for item in directory.iterdir():
                # Skip hidden directories
                if item.is_dir() and item.name.startswith('.'):
                    continue
                    
                # Skip excluded directories
                if item.is_dir() and item.name in self.excluded_dirs:
                    continue
                
                # Handle symbolic links based on configuration
                if item.is_symlink() and not self.follow_symlinks:
                    continue
                
                # Recursively process directories
                if item.is_dir():
                    yield from self._scan_recursive(item)
                    
                # Process Python files
                elif item.suffix.lower() == '.py':
                    if self._validate_python_file(item):
                        yield item
                        
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
    
    def _validate_python_file(self, file_path: pathlib.Path) -> bool:
        """
        Validate that a file is a proper Python source file with UTF-8 encoding.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is a valid Python file, False otherwise
        """
        try:
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                return False
                
            # Validate UTF-8 encoding by attempting to read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                # Just read a small chunk to validate encoding
                f.read(1024)
                
            return True
            
        except UnicodeDecodeError:
            # Not valid UTF-8
            return False
        except Exception:
            # Any other error reading the file
            return False


def get_python_files(
    directory: str,
    follow_symlinks: bool = False,
    excluded_dirs: Optional[Set[str]] = None
) -> List[pathlib.Path]:
    """
    Convenience function to get all Python files in a directory.
    
    Args:
        directory: Directory to scan
        follow_symlinks: Whether to follow symbolic links
        excluded_dirs: Additional directories to exclude
        
    Returns:
        List of paths to valid Python files
    """
    crawler = FileCrawler(
        follow_symlinks=follow_symlinks,
        excluded_dirs=excluded_dirs
    )
    return crawler.scan_directory(directory)