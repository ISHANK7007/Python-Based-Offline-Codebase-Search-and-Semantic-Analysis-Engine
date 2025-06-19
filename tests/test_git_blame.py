import os
import sqlite3
import subprocess
from models.code_element_git import GitMetadata  # Ensure this path is correct


class GitMetadataManager:
    def __init__(self, repo_path, cache_dir=".semantic-git-cache"):
        self.repo_path = repo_path
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.blame_cache = self._load_blame_cache()

    def _load_blame_cache(self):
        """Load or initialize the blame cache SQLite database."""
        cache_path = os.path.join(self.cache_dir, "blame_cache.db")
        conn = sqlite3.connect(cache_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS blame_data (
                file_path TEXT,
                line_start INTEGER,
                line_end INTEGER,
                commit_hash TEXT,
                author TEXT,
                timestamp INTEGER,
                PRIMARY KEY (file_path, line_start, line_end)
            )
        ''')
        return conn

    def get_git_metadata(self, file_path, line_start, line_end, mode="lazy"):
        """
        Get Git metadata for a code element.
        Modes:
        - 'eager': fetch immediately or use cache
        - 'lazy': fetch and cache now
        - 'placeholder': return a lazy-loader wrapper
        """
        if mode == "eager" or self._is_cached(file_path, line_start, line_end):
            return self._get_cached_blame(file_path, line_start, line_end)
        elif mode == "lazy":
            return self._fetch_and_cache_blame(file_path, line_start, line_end)
        elif mode == "placeholder":
            return GitMetadata(
                commit_hash="pending",
                lazy_loader=lambda: self._fetch_and_cache_blame(file_path, line_start, line_end)
            )
        else:
            raise ValueError(f"Unsupported git blame mode: {mode}")

    def _is_cached(self, file_path, line_start, line_end):
        """Check if blame data is already cached."""
        cursor = self.blame_cache.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM blame_data 
            WHERE file_path = ? AND line_start = ? AND line_end = ?
        ''', (file_path, line_start, line_end))
        return cursor.fetchone()[0] > 0

    def _get_cached_blame(self, file_path, line_start, line_end):
        """Retrieve cached blame data."""
        cursor = self.blame_cache.cursor()
        cursor.execute('''
            SELECT commit_hash, author, timestamp FROM blame_data 
            WHERE file_path = ? AND line_start = ? AND line_end = ?
        ''', (file_path, line_start, line_end))
        result = cursor.fetchone()
        if result:
            return GitMetadata(
                commit_hash=result[0],
                author=result[1],
                timestamp=result[2]
            )
        return GitMetadata()  # fallback default

    def _fetch_and_cache_blame(self, file_path, line_start, line_end):
        """Run git blame and store results in cache."""
        rel_path = os.path.relpath(file_path, self.repo_path)

        try:
            cmd = [
                "git", "-C", self.repo_path, "blame",
                "-L", f"{line_start},{line_end}",
                "--porcelain", rel_path
            ]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
            commit_hash, author, timestamp = self._parse_blame_output(output)

            cursor = self.blame_cache.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO blame_data 
                (file_path, line_start, line_end, commit_hash, author, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (file_path, line_start, line_end, commit_hash, author, timestamp))
            self.blame_cache.commit()

            return GitMetadata(
                commit_hash=commit_hash,
                author=author,
                timestamp=timestamp
            )

        except subprocess.CalledProcessError:
            return GitMetadata()

    def _parse_blame_output(self, output):
        """Parse output from `git blame --porcelain`."""
        lines = output.strip().splitlines()
        commit_hash = lines[0].split()[0]
        author = None
        timestamp = None

        for line in lines:
            if line.startswith("author "):
                author = line[7:]
            elif line.startswith("author-time "):
                timestamp = int(line[12:])
            if author and timestamp:
                break

        return commit_hash, author or "unknown", timestamp or 0
