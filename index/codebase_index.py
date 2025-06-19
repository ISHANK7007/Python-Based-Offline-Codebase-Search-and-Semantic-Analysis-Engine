# indexer/code_index.py
import os
import pickle
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Union, Iterator, Tuple, Any, TypeVar, Generic, Callable
from dataclasses import dataclass, field, asdict
from functools import lru_cache
import threading
from collections import defaultdict
import re
import time
from models import CodeElement, ElementType
from parser import ASTParser

# Type variable for generics
T = TypeVar('T', bound=CodeElement)

@dataclass
class ElementReference:
    """Lightweight reference to a CodeElement for lazy loading."""
    element_id: str
    element_type: ElementType
    name: str
    module_path: str
    file_path: Path
    line_range: Tuple[int, int]
    is_loaded: bool = False
    
    @classmethod
    def from_element(cls, element: CodeElement) -> 'ElementReference':
        """Create a reference from a full CodeElement."""
        return cls(
            element_id=f"{element.module_path}.{element.name}",
            element_type=element.element_type,
            name=element.name,
            module_path=element.module_path,
            file_path=element.file_path,
            line_range=(element.line_start, element.line_end)
        )


class CodebaseIndex:
    """
    Central index for code elements with optimized lookup and lazy loading.
    
    This class maintains references to all code elements and provides
    fast lookup capabilities while managing memory through lazy loading.
    """
    
    def __init__(self, 
                 lazy_loading: bool = True, 
                 cache_size: int = 1000,
                 search_index_all: bool = False):
        """
        Initialize the codebase index.
        
        Args:
            lazy_loading: Whether to use lazy loading
            cache_size: Size of the LRU cache for loaded elements
            search_index_all: Whether to build search index for all elements immediately
        """
        self.logger = logging.getLogger(__name__)
        
        # Core storage
        self._elements: Dict[str, Union[CodeElement, ElementReference]] = {}
        
        # Type-specific indexes for fast lookup
        self._modules: Dict[str, Set[str]] = {}  # module_path -> element_ids
        self._classes: Dict[str, str] = {}  # class_name -> element_id
        self._functions: Dict[str, str] = {}  # function_name -> element_id
        self._methods: Dict[str, Dict[str, str]] = defaultdict(dict)  # class_id -> {method_name -> element_id}
        
        # Path-based lookup
        self._file_elements: Dict[Path, Set[str]] = defaultdict(set)  # file_path -> element_ids
        
        # Search indexes
        self._token_index: Dict[str, Set[str]] = defaultdict(set)  # token -> element_ids
        self._name_trie = Trie()  # Prefix tree for name lookups
        
        # Relationship maps
        self._parent_children: Dict[str, Set[str]] = defaultdict(set)  # parent_id -> child_ids
        
        # Configuration
        self.lazy_loading = lazy_loading
        self.search_index_all = search_index_all
        
        # Caching
        self._element_cache = LRUCache(cache_size)
        
        # Concurrency control
        self._lock = threading.RLock()
        
        # Stats
        self.total_elements = 0
        self.loaded_elements = 0
    
    def add_element(self, element: CodeElement, force_full: bool = False) -> None:
        """
        Add an element to the index.
        
        Args:
            element: Code element to add
            force_full: If True, always store the full element (not a reference)
        """
        element_id = f"{element.module_path}.{element.name}"
        
        with self._lock:
            # Check for duplicates
            if element_id in self._elements:
                # Update if it's a reference and we have the full element
                if isinstance(self._elements[element_id], ElementReference) and not isinstance(element, ElementReference):
                    self._update_indexes(element_id, element)
                    self._elements[element_id] = element
                    self.loaded_elements += 1
                return
            
            # Store either the full element or just a reference based on lazy loading setting
            if self.lazy_loading and not force_full:
                self._elements[element_id] = ElementReference.from_element(element)
            else:
                self._elements[element_id] = element
                self.loaded_elements += 1
                
                # Index for search if requested
                if self.search_index_all:
                    self._index_element_for_search(element)
            
            # Update indexes
            self._update_indexes(element_id, element)
            
            # Track total elements
            self.total_elements += 1
    
    def _update_indexes(self, element_id: str, element: CodeElement) -> None:
        """Update all indexes with the element."""
        # Update module index
        if element.module_path:
            if element.module_path not in self._modules:
                self._modules[element.module_path] = set()
            self._modules[element.module_path].add(element_id)
        
        # Update type-specific indexes
        if element.element_type == ElementType.CLASS:
            self._classes[element.name] = element_id
        elif element.element_type == ElementType.FUNCTION:
            self._functions[element.name] = element_id
        elif element.element_type == ElementType.METHOD:
            # For methods, track both by class and globally
            if element.parent_name:
                parent_id = f"{element.module_path}.{element.parent_name}"
                self._methods[parent_id][element.name] = element_id
            self._functions[element.name] = element_id
        
        # Update file index
        self._file_elements[element.file_path].add(element_id)
        
        # Update relationship maps
        if element.parent_name:
            parent_id = f"{element.module_path}.{element.parent_name}"
            self._parent_children[parent_id].add(element_id)
            
        # Update name trie for prefix search
        self._name_trie.insert(element.name, element_id)
    
    def _index_element_for_search(self, element: CodeElement) -> None:
        """Add an element to the search index."""
        # Generate search tokens if needed
        if not element.search_tokens:
            element.generate_search_tokens()
            
        # Add to token index
        element_id = f"{element.module_path}.{element.name}"
        for token in element.search_tokens:
            if len(token) > 2:  # Skip very short tokens
                self._token_index[token].add(element_id)
    
    def get_element(self, element_id: str) -> Optional[CodeElement]:
        """
        Get an element by its ID, loading it if necessary.
        
        Args:
            element_id: Element ID
            
        Returns:
            CodeElement if found, None otherwise
        """
        with self._lock:
            if element_id not in self._elements:
                return None
            
            # Check if it's in the cache
            cached = self._element_cache.get(element_id)
            if cached is not None:
                return cached
            
            element = self._elements[element_id]
            
            # If it's a reference, we need to load the actual element
            if isinstance(element, ElementReference):
                return self._load_element(element)
                
            # If it's already a full element, just return it
            self._element_cache.put(element_id, element)
            return element
    
    @lru_cache(maxsize=128)
    def get_by_name(self, name: str, element_type: Optional[ElementType] = None) -> List[CodeElement]:
        """
        Get elements by name, optionally filtering by type.
        
        Args:
            name: Element name
            element_type: Optional element type filter
            
        Returns:
            List of matching elements
        """
        # For exact name match against type-specific indexes
        results = []
        
        with self._lock:
            # Check appropriate indexes based on type
            if element_type == ElementType.CLASS:
                if name in self._classes:
                    element = self.get_element(self._classes[name])
                    if element:
                        results.append(element)
                        
            elif element_type == ElementType.FUNCTION:
                if name in self._functions:
                    element = self.get_element(self._functions[name])
                    if element and element.element_type == ElementType.FUNCTION:
                        results.append(element)
                        
            elif element_type == ElementType.METHOD:
                if name in self._functions:
                    element = self.get_element(self._functions[name])
                    if element and element.element_type == ElementType.METHOD:
                        results.append(element)
                        
            # If no type filter or no results yet, try all indexes
            elif element_type is None:
                # Check classes
                if name in self._classes:
                    element = self.get_element(self._classes[name])
                    if element:
                        results.append(element)
                        
                # Check functions and methods
                if name in self._functions:
                    element = self.get_element(self._functions[name])
                    if element:
                        results.append(element)
        
        return results
    
    def get_by_prefix(self, prefix: str, max_results: int = 100) -> List[CodeElement]:
        """
        Get elements by name prefix.
        
        Args:
            prefix: Name prefix to search for
            max_results: Maximum number of results
            
        Returns:
            List of matching elements
        """
        element_ids = self._name_trie.find_prefix(prefix, max_results)
        return [self.get_element(eid) for eid in element_ids if self.get_element(eid) is not None]
    
    def search(self, query: str, element_type: Optional[ElementType] = None, max_results: int = 100) -> List[CodeElement]:
        """
        Search for elements matching the query.
        
        Args:
            query: Search query
            element_type: Optional type filter
            max_results: Maximum number of results
            
        Returns:
            List of matching elements
        """
        # Clean and tokenize the query
        tokens = set(re.findall(r'\w+', query.lower()))
        
        # Score map: element_id -> score
        scores = defaultdict(int)
        
        with self._lock:
            # For each token, find matching elements
            for token in tokens:
                if len(token) <= 2:
                    continue  # Skip very short tokens
                    
                # Exact token match
                if token in self._token_index:
                    for element_id in self._token_index[token]:
                        scores[element_id] += 3  # Higher score for exact matches
                
                # Partial token match (startswith)
                for idx_token, element_ids in self._token_index.items():
                    if idx_token.startswith(token):
                        for element_id in element_ids:
                            scores[element_id] += 2
                    elif token in idx_token:
                        for element_id in element_ids:
                            scores[element_id] += 1
        
        # Sort by score
        sorted_ids = sorted(scores.keys(), key=lambda eid: scores[eid], reverse=True)
        
        # Filter by type if requested
        if element_type is not None:
            filtered_ids = []
            for eid in sorted_ids:
                element = self.get_element(eid)
                if element and element.element_type == element_type:
                    filtered_ids.append(eid)
            sorted_ids = filtered_ids
        
        # Get top results
        results = []
        for eid in sorted_ids[:max_results]:
            element = self.get_element(eid)
            if element:
                results.append(element)
                
        return results
    
    def get_children(self, element_id: str) -> List[CodeElement]:
        """
        Get all child elements of an element.
        
        Args:
            element_id: Parent element ID
            
        Returns:
            List of child elements
        """
        with self._lock:
            if element_id not in self._parent_children:
                return []
            
            children = []
            for child_id in self._parent_children[element_id]:
                child = self.get_element(child_id)
                if child:
                    children.append(child)
                    
            return children
    
    def get_elements_in_file(self, file_path: Union[str, Path]) -> List[CodeElement]:
        """
        Get all elements defined in a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of elements in the file
        """
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        with self._lock:
            if path not in self._file_elements:
                return []
            
            elements = []
            for element_id in self._file_elements[path]:
                element = self.get_element(element_id)
                if element:
                    elements.append(element)
                    
            return elements
    
    def get_elements_in_module(self, module_path: str) -> List[CodeElement]:
        """
        Get all elements in a module.
        
        Args:
            module_path: Import path of the module
            
        Returns:
            List of elements in the module
        """
        with self._lock:
            if module_path not in self._modules:
                return []
            
            elements = []
            for element_id in self._modules[module_path]:
                element = self.get_element(element_id)
                if element:
                    elements.append(element)
                    
            return elements
    
    def _load_element(self, reference: ElementReference) -> Optional[CodeElement]:
        """
        Load a full element from a reference.
        
        Args:
            reference: Element reference
            
        Returns:
            Full CodeElement if successful, None otherwise
        """
        # If we're already at capacity, make room
        if self.loaded_elements >= self._element_cache.capacity:
            self._element_cache.evict_oldest()
            
        # Parse the file and extract just this element
        try:
            parser = ASTParser()
            file_elements = parser.parse_file(reference.file_path)
            
            # Find our element
            for element_id, element in file_elements.items():
                if (element.name == reference.name and 
                    element.element_type == reference.element_type and 
                    element.line_start == reference.line_range[0]):
                    
                    # Update our index with the full element
                    self._elements[element_id] = element
                    self._element_cache.put(element_id, element)
                    self.loaded_elements += 1
                    
                    # Add to search index if needed
                    self._index_element_for_search(element)
                    
                    return element
            
            # If we didn't find the exact element, return None
            self.logger.warning(f"Failed to load element: {reference.element_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading element {reference.element_id}: {e}")
            return None
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """
        Save the index to a file.
        
        Args:
            file_path: Path to save to
        """
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        # Ensure we're saving with a .idx extension
        if path.suffix != '.idx':
            path = path.with_suffix('.idx')
            
        with self._lock:
            # Convert all elements to a serializable format
            serializable_elements = {}
            for element_id, element in self._elements.items():
                if isinstance(element, ElementReference):
                    # For references, store the reference data
                    serializable_elements[element_id] = {
                        'type': 'reference',
                        'data': asdict(element)
                    }
                else:
                    # For full elements, store as dict
                    serializable_elements[element_id] = {
                        'type': 'element',
                        'data': element.to_dict()
                    }
            
            # Prepare the full index data
            index_data = {
                'elements': serializable_elements,
                'modules': {k: list(v) for k, v in self._modules.items()},
                'classes': self._classes,
                'functions': self._functions,
                'methods': {k: dict(v) for k, v in self._methods.items()},
                'file_elements': {str(k): list(v) for k, v in self._file_elements.items()},
                'parent_children': {k: list(v) for k, v in self._parent_children.items()},
                'token_index': {k: list(v) for k, v in self._token_index.items()},
                'stats': {
                    'total_elements': self.total_elements,
                    'loaded_elements': self.loaded_elements
                }
            }
            
            # Save to file
            with open(path, 'wb') as f:
                pickle.dump(index_data, f)
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path], lazy_loading: bool = True) -> 'CodebaseIndex':
        """
        Load an index from a file.
        
        Args:
            file_path: Path to load from
            lazy_loading: Whether to use lazy loading
            
        Returns:
            Loaded CodebaseIndex
        """
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        # Ensure we're loading from a .idx file
        if path.suffix != '.idx':
            path = path.with_suffix('.idx')
            
        with open(path, 'rb') as f:
            index_data = pickle.load(f)
        
        # Create a new index
        index = cls(lazy_loading=lazy_loading)
        
        # Restore index data
        for element_id, element_data in index_data['elements'].items():
            if element_data['type'] == 'reference':
                # Create a reference
                ref_data = element_data['data']
                reference = ElementReference(
                    element_id=ref_data['element_id'],
                    element_type=ElementType[ref_data['element_type']],
                    name=ref_data['name'],
                    module_path=ref_data['module_path'],
                    file_path=Path(ref_data['file_path']),
                    line_range=tuple(ref_data['line_range']),
                    is_loaded=ref_data['is_loaded']
                )
                index._elements[element_id] = reference
            else:
                # We'd need to reconstruct the proper CodeElement subclass here
                # For simplicity, we'll just keep references and load on demand
                # This could be expanded to fully reconstruct elements if needed
                pass
        
        # Restore indexes
        index._modules = {k: set(v) for k, v in index_data['modules'].items()}
        index._classes = index_data['classes']
        index._functions = index_data['functions']
        index._methods = defaultdict(dict)
        for k, v in index_data['methods'].items():
            index._methods[k] = v
            
        index._file_elements = defaultdict(set)
        for k, v in index_data['file_elements'].items():
            index._file_elements[Path(k)] = set(v)
            
        index._parent_children = defaultdict(set)
        for k, v in index_data['parent_children'].items():
            index._parent_children[k] = set(v)
            
        index._token_index = defaultdict(set)
        for k, v in index_data['token_index'].items():
            index._token_index[k] = set(v)
            
        # Restore stats
        index.total_elements = index_data['stats']['total_elements']
        index.loaded_elements = 0  # We're not loading any elements fully
        
        # Rebuild trie
        index._name_trie = Trie()
        for element_id, element_data in index_data['elements'].items():
            name = element_data['data']['name']
            index._name_trie.insert(name, element_id)
            
        return index
    
    def build_index_from_directory(self, directory: Union[str, Path], 
                                  batch_size: int = 100, 
                                  max_memory_mb: int = 500) -> None:
        """
        Build the index from a directory.
        
        Args:
            directory: Directory to index
            batch_size: Number of files to process in each batch
            max_memory_mb: Maximum memory to use in MB
        """
        from ..scanner import FileCrawler, get_python_files_batched
        from parser import ASTParser
        
        dir_path = Path(directory) if isinstance(directory, str) else directory
        
        # Track progress
        start_time = time.time()
        files_processed = 0
        elements_found = 0
        
        # Create parser
        parser = ASTParser()
        
        # Process files in batches
        with get_python_files_batched(str(dir_path), batch_size=batch_size) as batches:
            for batch in batches:
                batch_elements = 0
                
                # Process each file in the batch
                for file_path in batch:
                    # Parse the file
                    file_elements = parser.parse_file(file_path)
                    
                    # Add elements to index
                    for element_id, element in file_elements.items():
                        self.add_element(element)
                        batch_elements += 1
                
                # Update stats
                files_processed += len(batch)
                elements_found += batch_elements
                
                # Log progress
                elapsed = time.time() - start_time
                self.logger.info(f"Processed {files_processed} files, found {elements_found} elements in {elapsed:.2f}s")
                
                # Check memory usage if requested
                if max_memory_mb > 0:
                    # This is a simplified approach - a real implementation would
                    # monitor actual memory usage and take action if needed
                    if self.loaded_elements > (max_memory_mb * 1024 * 1024) / 1000:  # Rough estimate
                        self._element_cache.clear()
                        # Force garbage collection in a real implementation
        
        # Final stats
        total_time = time.time() - start_time
        self.logger.info(f"Indexing complete: {files_processed} files, {elements_found} elements in {total_time:.2f}s")
    
    def clear(self) -> None:
        """Clear the index."""
        with self._lock:
            self._elements.clear()
            self._modules.clear()
            self._classes.clear()
            self._functions.clear()
            self._methods.clear()
            self._file_elements.clear()
            self._token_index.clear()
            self._name_trie = Trie()
            self._parent_children.clear()
            self._element_cache.clear()
            self.total_elements = 0
            self.loaded_elements = 0


# Helper classes

class LRUCache:
    """Simple LRU cache implementation."""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache = {}
        self._usage_list = []
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache."""
        with self._lock:
            if key not in self._cache:
                return None
                
            # Update usage order
            self._usage_list.remove(key)
            self._usage_list.append(key)
            
            return self._cache[key]
    
    def put(self, key: str, value: Any) -> None:
        """Add an item to the cache."""
        with self._lock:
            # If key exists, update usage
            if key in self._cache:
                self._usage_list.remove(key)
            elif len(self._cache) >= self.capacity:
                # Make room by removing oldest item
                self.evict_oldest()
                
            # Add new item
            self._cache[key] = value
            self._usage_list.append(key)
    
    def evict_oldest(self) -> None:
        """Remove the oldest item from the cache."""
        with self._lock:
            if not self._usage_list:
                return
                
            oldest = self._usage_list.pop(0)
            if oldest in self._cache:
                del self._cache[oldest]
    
    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._usage_list.clear()


class TrieNode:
    """Node in a trie (prefix tree)."""
    
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.element_ids = set()


class Trie:
    """
    Trie (prefix tree) for efficient prefix searches.
    """
    
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str, element_id: str) -> None:
        """Insert a word and associated element ID into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.element_ids.add(element_id)
    
    def find_prefix(self, prefix: str, max_results: int = 100) -> List[str]:
        """Find all element IDs with the given prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # DFS to find all words with this prefix
        results = []
        self._collect_ids(node, results, max_results)
        return results
    
    def _collect_ids(self, node: TrieNode, results: List[str], max_results: int) -> bool:
        """Collect element IDs from a node and its children."""
        if node.is_end:
            results.extend(node.element_ids)
            
        if len(results) >= max_results:
            return False
            
        for child_node in node.children.values():
            if not self._collect_ids(child_node, results, max_results):
                return False
                
        return True