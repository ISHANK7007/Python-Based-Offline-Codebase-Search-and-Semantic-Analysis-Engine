import sqlite3

class SemanticHashEvolution:
    def __init__(self, db_path=".semantic-evolution.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_hash_history (
                symbol_path TEXT,            -- Fully qualified symbol name
                semantic_hash TEXT,          -- Semantic fingerprint
                commit_hash TEXT,            -- Git commit where this version exists
                timestamp INTEGER,           -- Commit timestamp (Unix epoch)
                parent_semantic_hash TEXT,   -- Previous semantic hash (if any)
                PRIMARY KEY (symbol_path, commit_hash)
            )
        ''')
        # Useful indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_semantic_hash ON semantic_hash_history(semantic_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_commit_hash ON semantic_hash_history(commit_hash)')
        self.conn.commit()

    def record_change(self, symbol, semantic_hash, commit_hash, timestamp, parent_semantic_hash=None):
        """
        Record a new semantic version of a symbol in the evolution history.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO semantic_hash_history (
                symbol_path, semantic_hash, commit_hash, timestamp, parent_semantic_hash
            ) VALUES (?, ?, ?, ?, ?)
        ''', (symbol, semantic_hash, commit_hash, timestamp, parent_semantic_hash))
        self.conn.commit()

    def get_history(self, symbol_path):
        """
        Get the full semantic history of a symbol.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT commit_hash, semantic_hash, parent_semantic_hash, timestamp
            FROM semantic_hash_history
            WHERE symbol_path = ?
            ORDER BY timestamp ASC
        ''', (symbol_path,))
        return cursor.fetchall()
