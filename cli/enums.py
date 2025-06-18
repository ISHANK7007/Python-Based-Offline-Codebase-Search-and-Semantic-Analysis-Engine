# cli/enums.py
from enum import Enum

class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    CSV = "csv"

class VerbosityLevel(str, Enum):
    BASIC = "basic"
    DETAILED = "detailed"
