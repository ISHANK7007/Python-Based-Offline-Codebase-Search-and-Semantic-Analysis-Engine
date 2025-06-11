# models/code_element.py
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Set
from pathlib import Path
import ast
from models.enums import ElementType


class ElementType(Enum):
    """Enumeration of code element types."""
    CLASS = auto()
    FUNCTION = auto()
    METHOD = auto()
    IMPORT = auto()
    MODULE = auto()
    VARIABLE = auto()


class ElementKind(Enum):
    """More granular classification of elements."""
    DECLARATION = auto()
    DEFINITION = auto()
    USAGE = auto()
    TYPE_HINT = auto()


@dataclass
class CodeElement:
    """Base class for all code elements found in Python source files."""
    name: str
    element_type: ElementType
    file_path: Path
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    parent_name: Optional[str] = None
    module_path: str = ""
    ast_node: Optional[ast.AST] = field(default=None, repr=False, compare=False)
    search_tokens: Set[str] = field(default_factory=set)

    def generate_search_tokens(self) -> None:
        tokens = set()
        tokens.add(self.name.lower())
        if self.docstring:
            tokens.update(word.lower() for word in self.docstring.split() if len(word) > 2)
        if self.module_path:
            tokens.update(part.lower() for part in self.module_path.split('.'))
        self.search_tokens = tokens

    def to_dict(self) -> Dict:
        result = {
            "name": self.name,
            "type": self.element_type.name,
            "file_path": str(self.file_path),
            "line_range": [self.line_start, self.line_end],
            "docstring": self.docstring,
            "decorators": self.decorators,
            "module_path": self.module_path,
        }
        if self.parent_name:
            result["parent"] = self.parent_name
        return result


@dataclass
class FunctionElement(CodeElement):
    parameters: List[Dict] = field(default_factory=list)
    return_annotation: Optional[str] = None
    is_async: bool = False
    is_method: bool = False
    is_static: bool = False
    is_class_method: bool = False
    is_property: bool = False

    def __post_init__(self):
        self.element_type = ElementType.METHOD if self.is_method else ElementType.FUNCTION

    def to_dict(self) -> Dict:
        result = super().to_dict()
        result.update({
            "parameters": self.parameters,
            "return_type": self.return_annotation,
            "is_async": self.is_async
        })
        if self.is_method:
            result.update({
                "is_static": self.is_static,
                "is_class_method": self.is_class_method,
                "is_property": self.is_property
            })
        return result

    def generate_search_tokens(self) -> None:
        super().generate_search_tokens()
        for param in self.parameters:
            self.search_tokens.add(param.get("name", "").lower())
            if annotation := param.get("annotation"):
                self.search_tokens.add(annotation.lower())
        if self.return_annotation:
            self.search_tokens.add(self.return_annotation.lower())


@dataclass
class ClassElement(CodeElement):
    bases: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.element_type = ElementType.CLASS

    def to_dict(self) -> Dict:
        result = super().to_dict()
        result.update({
            "bases": self.bases,
            "methods": self.methods,
            "attributes": self.attributes
        })
        return result

    def generate_search_tokens(self) -> None:
        super().generate_search_tokens()
        for base in self.bases:
            self.search_tokens.add(base.lower())
        for method in self.methods:
            self.search_tokens.add(method.lower())
        for name, type_hint in self.attributes.items():
            self.search_tokens.add(name.lower())
            if type_hint:
                self.search_tokens.add(type_hint.lower())


@dataclass
class ImportElement(CodeElement):
    source_module: str = ""
    import_names: List[str] = field(default_factory=list)
    import_aliases: Dict[str, str] = field(default_factory=dict)
    is_from_import: bool = False

    def __post_init__(self):
        self.element_type = ElementType.IMPORT

    def to_dict(self) -> Dict:
        result = super().to_dict()
        result.update({
            "source": self.source_module,
            "imports": self.import_names,
            "aliases": self.import_aliases,
            "is_from_import": self.is_from_import
        })
        return result

    def generate_search_tokens(self) -> None:
        super().generate_search_tokens()
        self.search_tokens.update(part.lower() for part in self.source_module.split('.'))
        self.search_tokens.update(name.lower() for name in self.import_names)
        self.search_tokens.update(alias.lower() for alias in self.import_aliases.values())


@dataclass
class ModuleElement(CodeElement):
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    is_package: bool = False

    def __post_init__(self):
        self.element_type = ElementType.MODULE
