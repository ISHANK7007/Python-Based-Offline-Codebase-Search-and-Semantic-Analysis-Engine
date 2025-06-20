# codebase_index.py
class CodebaseIndex:
    # ... existing methods ...
    
    def index_with_git_metadata(self, repo_path, **options):
        """Index codebase with git metadata attached to each element"""
        git_enabled = options.get('git_metadata', False)
        # ... existing indexing logic with added git metadata ...