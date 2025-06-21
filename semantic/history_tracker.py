from datetime import datetime, timedelta
import time

class QueryEngine:
    def __init__(self, index):
        self.index = index  # Expects CodebaseIndex or similar

    def find_by_git_author(self, author_name):
        """
        Return elements authored by the given person (case-insensitive match).
        """
        return [
            element for element in self.index.elements.values()
            if hasattr(element, "git_metadata") and
               element.git_metadata and
               element.git_metadata.author and
               author_name.lower() in element.git_metadata.author.lower()
        ]

    def find_recent_changes(self, days=7):
        """
        Return elements modified within the last N days (based on Git timestamp).
        """
        now = int(time.time())
        threshold = now - (days * 86400)

        return [
            element for element in self.index.elements.values()
            if hasattr(element, "git_metadata") and
               element.git_metadata and
               isinstance(element.git_metadata.timestamp, int) and
               element.git_metadata.timestamp >= threshold
        ]
