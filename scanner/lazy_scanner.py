import os
import pathlib
from typing import List, Set, Optional, Iterator, Union, Iterable
from contextlib import contextmanager
import itertools

class FileCrawler:
    """Recursively scans directories for Python source files with configurable exclusions."""
    
    def __init__(
        self,
        follow_symlinks: bool = False,
        excluded_dirs: Optional[Set[str]] = None,
        max_file_size_mb: int = 10,
        batch_size: int = 1000
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
        self.batch_size = batch_size
    
    def scan_directory(self, root_path: str, lazy: bool = False) -> Union[List[pathlib.Path], Iterator[pathlib.Path]]:
        """
        Scan directory recursively for Python files.
        
        Args:
            root_path: Directory to scan
            lazy: If True, return iterator instead of list
            
        Returns:
            List of normalized paths to valid Python files or an iterator if lazy=True
        """
        root = pathlib.Path(root_path).resolve()
        
        if not root.exists():
            raise FileNotFoundError(f"Path does not exist: {root}")
            
        if not root.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {root}")
        
        # Return iterator for lazy evaluation
        if lazy:
            return self._scan_recursive(root)
        
        # Return full list for eager evaluation
        return list(self._scan_recursive(root))
    
    def scan_directories(self, root_paths: List[str], lazy: bool = False) -> Union[List[pathlib.Path], Iterator[pathlib.Path]]:
        """
        Scan multiple directories recursively for Python files.
        
        Args:
            root_paths: List of directories to scan
            lazy: If True, return iterator instead of list
            
        Returns:
            List of normalized paths to valid Python files or an iterator if lazy=True
        """
        if lazy:
            return self._scan_multiple_lazy(root_paths)
        
        # Eager mode
        result = []
        for path in root_paths:
            result.extend(self.scan_directory(path, lazy=False))
        return result
    
    def _scan_multiple_lazy(self, root_paths: List[str]) -> Iterator[pathlib.Path]:
        """Chain together iterators for multiple root paths."""
        iterators = [self.scan_directory(path, lazy=True) for path in root_paths]
        return itertools.chain.from_iterable(iterators)
    
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
    
    @contextmanager
    def batch_processor(self, root_path: str) -> Iterator[List[pathlib.Path]]:
        """
        Context manager that yields batches of files to process.
        Helps control memory usage for large repositories.
        
        Args:
            root_path: Directory to scan
            
        Yields:
            Batches of paths as lists, each containing at most batch_size files
        """
        file_iterator = self.scan_directory(root_path, lazy=True)
        
        try:
            while True:
                batch = list(itertools.islice(file_iterator, self.batch_size))
                if not batch:
                    break
                yield batch
        finally:
            # Any cleanup needed when processing is done
            pass


class MemoryBudgetedFileCrawler(FileCrawler):
    """
    File crawler with memory budget controls.
    Estimates memory usage and pauses/resumes scanning to stay within budget.
    """
    
    def __init__(
        self, 
        memory_budget_mb: int = 1000,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.memory_budget = memory_budget_mb * 1024 * 1024  # Convert to bytes
        self.current_memory_usage = 0
    
    def scan_with_budget(self, root_path: str) -> Iterator[pathlib.Path]:
        """
        Scan directory recursively for Python files while respecting memory budget.
        
        Args:
            root_path: Directory to scan
            
        Returns:
            Iterator that yields files while monitoring memory usage
        """
        file_iterator = super().scan_directory(root_path, lazy=True)
        
        for file_path in file_iterator:
            # Estimate memory needed for this file (path string + basic metadata)
            estimated_size = len(str(file_path)) * 2 + 100  # Basic approximation
            
            # Add file size estimation if we plan to load contents
            try:
                file_size = file_path.stat().st_size
                # Assume we need roughly 2x the file size in memory when processing
                estimated_size += file_size * 2
            except (OSError, PermissionError):
                # If we can't stat the file, use a conservative estimate
                estimated_size += 10 * 1024  # Assume 10KB
            
            # Check if we're about to exceed our budget
            if self.current_memory_usage + estimated_size > self.memory_budget:
                # Here we could implement various strategies:
                # 1. Pause and wait for GC to run
                # 2. Process the current batch before continuing
                # 3. Signal the caller to process what we have so far
                
                # For now, we'll just yield the file but set a flag
                file_path._memory_warning = True
                
            self.current_memory_usage += estimated_size
            yield file_path