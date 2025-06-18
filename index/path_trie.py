class PathTrie:
    def __init__(self):
        self.root = {}
        self.files_at_node = {}  # node_id → list of files
    
    def insert(self, path, file_data):
        parts = path.split('/')
        current = self.root
        path_so_far = ""
        
        for part in parts:
            path_so_far += part + "/"
            if part not in current:
                current[part] = {}
            current = current[part]
            
            # Store file data at this node
            if path_so_far not in self.files_at_node:
                self.files_at_node[path_so_far] = []
            self.files_at_node[path_so_far].append(file_data)