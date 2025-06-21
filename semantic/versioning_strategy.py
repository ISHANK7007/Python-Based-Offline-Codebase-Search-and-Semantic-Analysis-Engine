import hashlib
import json

class SemanticHasher:
    @staticmethod
    def compute_hash(code_element):
        """Generate deterministic hash from element's semantic properties"""
        normalized = SemanticHasher._normalize_element(code_element)
        return hashlib.sha256(normalized.encode()).hexdigest()

    @staticmethod
    def _normalize_element(element):
        """Create normalized semantic fingerprint for a code element"""
        def safe_str(val):
            return str(val).strip() if val is not None else ""

        normalized_payload = {
            "name": safe_str(getattr(element, "name", "")),
            "parameters": safe_str(getattr(element, "parameters", "")),
            "returns": safe_str(getattr(element, "returns", "")),
            "decorators": sorted(getattr(element, "decorators", [])),
            "docstring": safe_str(getattr(element, "docstring", "")),
            "body": safe_str(getattr(element, "body_hash", "")),  # pre-hashed body if available
            "type": safe_str(getattr(element, "type", ""))  # e.g., function/class/module
        }

        return json.dumps(normalized_payload, sort_keys=True)
