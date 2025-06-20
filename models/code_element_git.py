class GitMetadata:
    def __init__(self, commit_hash=None, author=None, timestamp=None, diff_context=None):
        self.commit_hash = commit_hash  # Last commit that modified this element
        self.author = author            # Author of last change
        self.timestamp = timestamp      # When the change occurred
        self.diff_context = diff_context  # Summary of what changed (optional)
        self.history = []               # Optional historical changes array