import hashlib
import json

def compute_hash(code_element):
    """
    Compute a semantic hash for a code element.
    This includes name, parameters, return type, decorators, and docstring.
    """
    def safe_str(obj):
        return str(obj) if obj is not None else ""

    payload = {
        "name": safe_str(code_element.name),
        "parameters": safe_str(getattr(code_element, "parameters", "")),
        "returns": safe_str(getattr(code_element, "returns", "")),
        "decorators": safe_str(getattr(code_element, "decorators", "")),
        "docstring": safe_str(getattr(code_element, "docstring", "")),
        "body_hash": safe_str(getattr(code_element, "body_hash", "")),
    }

    json_data = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(json_data.encode()).hexdigest()
