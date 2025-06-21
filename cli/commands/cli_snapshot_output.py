import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable
import random
import time

class GitRepoEvolver:
    """Tool for creating synthetic Git repositories with controlled evolution."""
    
    def __init__(self, repo_path: Union[str, Path], seed: Optional[int] = None):
        """Initialize a Git repository evolver.
        
        Args:
            repo_path: Path where the repository will be created
            seed: Random seed for reproducible evolutions
        """
        self.repo_path = Path(repo_path)
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self._init_repo()
        
        # Set random seed for reproducibility
        if seed is not None:
            random.seed(seed)
        
    def _init_repo(self) -> None:
        """Initialize a Git repository if it doesn't exist."""
        if not (self.repo_path / ".git").exists():
            subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
            
            # Configure Git author for reproducible commits
            subprocess.run(
                ["git", "config", "user.name", "Semantic Indexer Test"],
                cwd=self.repo_path, check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "test@semantic-indexer.org"],
                cwd=self.repo_path, check=True
            )
            
            # Create initial readme
            readme = self.repo_path / "README.md"
            readme.write_text("# Test Repository\n\nThis repository was generated for testing purposes.\n")
            
            # Initial commit
            self._commit_changes("Initial commit")
    
    def _commit_changes(self, message: str) -> str:
        """Commit current changes to the repository.
        
        Args:
            message: Commit message
            
        Returns:
            Commit hash
        """
        subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path, check=True)
        
        # Get the commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    
    def create_branch(self, name: str) -> None:
        """Create and switch to a new branch.
        
        Args:
            name: Branch name
        """
        subprocess.run(["git", "checkout", "-b", name], cwd=self.repo_path, check=True)
    
    def switch_branch(self, name: str) -> None:
        """Switch to an existing branch.
        
        Args:
            name: Branch name
        """
        subprocess.run(["git", "checkout", name], cwd=self.repo_path, check=True)
    
    def create_tag(self, name: str, message: Optional[str] = None) -> None:
        """Create a tag at the current commit.
        
        Args:
            name: Tag name
            message: Optional tag message
        """
        if message:
            subprocess.run(
                ["git", "tag", "-a", name, "-m", message],
                cwd=self.repo_path, check=True
            )
        else:
            subprocess.run(["git", "tag", name], cwd=self.repo_path, check=True)
    
    def list_commits(self, branch: Optional[str] = None) -> List[Dict[str, str]]:
        """List commits in chronological order.
        
        Args:
            branch: Optional branch name
            
        Returns:
            List of commit dictionaries with hash, author, date, and message
        """
        cmd = ["git", "log", "--pretty=format:%H|%an|%ad|%s", "--date=iso"]
        if branch:
            cmd.append(branch)
            
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
        
        commits = []
        for line in result.stdout.split('\n'):
            if not line.strip():
                continue
            hash, author, date, message = line.split('|', 3)
            commits.append({
                "hash": hash,
                "author": author,
                "date": date,
                "message": message
            })
        
        return commits
    
    def add_file(self, path: str, content: str) -> None:
        """Add a new file to the repository.
        
        Args:
            path: Relative file path
            content: File content
        """
        file_path = self.repo_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
    
    def update_file(self, path: str, content: str) -> None:
        """Update an existing file.
        
        Args:
            path: Relative file path
            content: New file content
        """
        file_path = self.repo_path / path
        if file_path.exists():
            file_path.write_text(content)
        else:
            raise FileNotFoundError(f"File {path} not found")
    
    def remove_file(self, path: str) -> None:
        """Remove a file from the repository.
        
        Args:
            path: Relative file path
        """
        file_path = self.repo_path / path
        if file_path.exists():
            file_path.unlink()
        else:
            raise FileNotFoundError(f"File {path} not found")
    
    def batch_changes(self, changes: List[Dict[str, Any]], commit_message: str) -> str:
        """Apply multiple changes and commit them.
        
        Args:
            changes: List of change operations
            commit_message: Commit message
            
        Returns:
            Commit hash
        """
        for change in changes:
            operation = change["operation"]
            path = change["path"]
            
            if operation == "add":
                self.add_file(path, change["content"])
            elif operation == "update":
                self.update_file(path, change["content"])
            elif operation == "remove":
                self.remove_file(path)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        
        return self._commit_changes(commit_message)