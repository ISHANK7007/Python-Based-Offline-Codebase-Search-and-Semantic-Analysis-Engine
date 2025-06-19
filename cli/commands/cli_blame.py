import os
import subprocess
from index.codebase_index import CodebaseIndex
from semantic.function_fingerprint import SemanticHasher  # Adjust path as needed


class GitHistoryAnalyzer:
    def __init__(self, repo_path, evolution_db):
        self.repo_path = repo_path
        self.evolution_db = evolution_db

    def analyze_commit_range(self, start_commit, end_commit='HEAD'):
        """Analyze semantic changes over a commit range."""
        # Store current commit to restore later
        original_commit = subprocess.check_output(
            ["git", "-C", self.repo_path, "rev-parse", "HEAD"]
        ).decode().strip()

        try:
            # Get all commits in chronological order
            cmd = ["git", "-C", self.repo_path, "rev-list", "--reverse", f"{start_commit}..{end_commit}"]
            commits = subprocess.check_output(cmd).decode().strip().splitlines()

            prev_index = None

            for commit in commits:
                # Checkout the commit safely
                subprocess.check_call(["git", "-C", self.repo_path, "checkout", commit, "-q"])

                # Index the code at this commit
                current_index = self._index_code_at_commit()

                if prev_index:
                    self._record_semantic_changes(prev_index, current_index, commit)

                prev_index = current_index

        finally:
            # Restore original commit
            subprocess.check_call(["git", "-C", self.repo_path, "checkout", original_commit, "-q"])

    def _index_code_at_commit(self):
        """Index the current working directory at the checked-out commit."""
        indexer = CodebaseIndex(repo_path=self.repo_path)
        return indexer.index_codebase()

    def _record_semantic_changes(self, prev_index, current_index, commit):
        """Compare two semantic indexes and record any symbol-level changes."""
        all_symbols = set(prev_index.elements.keys()) | set(current_index.elements.keys())

        for symbol in all_symbols:
            prev_element = prev_index.elements.get(symbol)
            curr_element = current_index.elements.get(symbol)

            if prev_element and curr_element:
                prev_hash = SemanticHasher.compute_hash(prev_element)
                curr_hash = SemanticHasher.compute_hash(curr_element)

                if prev_hash != curr_hash:
                    self.evolution_db.record_change(
                        symbol=symbol,
                        semantic_hash=curr_hash,
                        commit_hash=commit,
                        timestamp=self._get_commit_timestamp(commit),
                        parent_semantic_hash=prev_hash
                    )

            elif curr_element and not prev_element:
                # Symbol added
                curr_hash = SemanticHasher.compute_hash(curr_element)
                self.evolution_db.record_change(
                    symbol=symbol,
                    semantic_hash=curr_hash,
                    commit_hash=commit,
                    timestamp=self._get_commit_timestamp(commit),
                    parent_semantic_hash=None
                )
            # If symbol was removed, skip (absence is natural)

    def _get_commit_timestamp(self, commit):
        """Return UNIX timestamp of the given commit."""
        cmd = ["git", "-C", self.repo_path, "show", "-s", "--format=%ct", commit]
        return int(subprocess.check_output(cmd).decode().strip())
