import re

def normalize_output(output: str) -> str:
    """Normalize CLI output by removing dynamic content and trimming whitespace."""
    lines = output.strip().splitlines()
    normalized = []
    for line in lines:
        # Remove ANSI escape sequences (colors, bold, etc.)
        line = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
        # Normalize spacing
        line = line.strip()
        if line:
            normalized.append(line)
    return "\n".join(normalized)

def normalize_golden(golden: str) -> str:
    """Normalize golden file content for comparison."""
    lines = golden.strip().splitlines()
    normalized = []
    for line in lines:
        # Strip leading/trailing spaces and remove empty lines
        line = line.strip()
        if line:
            normalized.append(line)
    return "\n".join(normalized)
