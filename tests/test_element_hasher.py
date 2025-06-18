from index.codebase_index import CodebaseIndex
from models.code_element import CodeElementId
from typing import List, Dict

# Placeholder: Define your real extraction function
def extract_elements_from_file(file_path: str) -> List[Dict]:
    """
    Simulate code element extraction.
    Replace this with your real AST or visitor-based logic.
    """
    return [
        {
            "type": "function",
            "name": "my_function",
            "file_path": file_path,
            "start_line": 10,
            "end_line": 20,
            "body": "def my_function():\n    pass",
            "decorators": [{"name": "@admin_required"}],
        }
    ]

# Create the CodebaseIndex
index = CodebaseIndex()

# Step 1: Process the file initially
file_path = "/path/to/file.py"
elements = extract_elements_from_file(file_path)
index.process_file(file_path, elements)

# Step 2: Re-process file incrementally (e.g. after user edits)
updated_elements = extract_elements_from_file(file_path)
index.process_file_incremental(file_path, updated_elements)

# Step 3: Query functions by semantic role or decorator
entrypoints = index.role_index.get("entrypoint", [])
admin_required_functions = index.decorator_index.get("@admin_required", [])

# Step 4: Check for existence of a specific function
function_id = CodeElementId(
    file_path="/path/to/file.py",
    element_type="FunctionElement",
    name="my_function",
    start_line=10,
    end_line=20
)

exists = index.registry.get_by_id(function_id) is not None
print(f"Function 'my_function' exists in registry? {exists}")
