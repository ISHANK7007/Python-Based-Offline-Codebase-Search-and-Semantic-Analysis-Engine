from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from .code_element import CodeElement
from .semantic_nodes import ElementType, ElementKind
from .syntax_nodes import FunctionNodeInfo


@dataclass
class ParameterSignature:
    name: str
    type_annotation: Optional[str] = None
    default_value: Optional[str] = None
    is_keyword_only: bool = False
    is_positional_only: bool = False
    is_variadic: bool = False
    description: Optional[str] = None

    def is_required(self) -> bool:
        return self.default_value is None and not self.is_variadic


@dataclass
class FunctionSignature:
    parameters: List[ParameterSignature]
    return_type: Optional[str] = None
    is_async: bool = False
    is_generator: bool = False
    is_abstract: bool = False

    def get_required_params_count(self) -> int:
        return sum(1 for param in self.parameters if param.is_required())

    def has_variadic_params(self) -> bool:
        return any(param.is_variadic for param in self.parameters)


@dataclass
class FunctionElement(CodeElement):
    signature: FunctionSignature
    is_method: bool = False
    is_static: bool = False
    is_class_method: bool = False
    is_property: bool = False
    is_constructor: bool = False
    is_overridden: bool = False
    is_override: bool = False
    return_annotation: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)

    # ✅ Required field for semantic validation
    semantic_traits: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # ✅ Runtime verification print for debug
        print("[OK] FunctionElement loaded from:", self.__module__)

        print("[OK] semantic_traits exists:", hasattr(self, "semantic_traits"))


        if not hasattr(self, 'id') or not getattr(self, 'id', None):
            self.id = f"{self.module_path or 'unknown'}:{self.name}"
        if not hasattr(self, 'qualified_name') or not getattr(self, 'qualified_name', None):
            self.qualified_name = f"{self.module_path}.{self.name}" if self.module_path else self.name

    @classmethod
    def from_syntax_node(
        cls,
        node_info: FunctionNodeInfo,
        element_id: str,
        qualified_name: str,
        module_path: str,
        parent_id: Optional[str] = None
    ) -> 'FunctionElement':
        is_method = parent_id is not None

        element_kind = ElementKind.DECLARATION
        if node_info.name == "__init__":
            element_kind = ElementKind.DEFINITION

        parameters = [
            ParameterSignature(
                name=arg.name,
                type_annotation=arg.annotation_str,
                default_value=arg.default_value_str,
                is_keyword_only=arg.is_keyword_only,
                is_positional_only=arg.is_positional_only,
                is_variadic=arg.is_variadic
            )
            for arg in node_info.args
        ]

        signature = FunctionSignature(
            parameters=parameters,
            return_type=node_info.return_annotation_str,
            is_async=node_info.is_async
        )

        element = cls(
            name=node_info.name,
            element_type=ElementType.METHOD if is_method else ElementType.FUNCTION,
            element_kind=element_kind,
            location=node_info.location,
            docstring=node_info.docstring,
            module_path=module_path,
            parent_id=parent_id,
            signature=signature,
            is_method=is_method,
            is_static=getattr(element_kind, 'name', '') == "STATICMETHOD",
            is_class_method=element_kind == ElementKind.CLASSMETHOD,
            is_property=element_kind == ElementKind.PROPERTY,
            is_constructor=element_kind == ElementKind.CONSTRUCTOR,
            decorators=node_info.decorator_names
        )

        element.id = element_id
        return element

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "signature": {
                "parameters": [self._param_to_dict(p) for p in self.signature.parameters],
                "return_type": self.signature.return_type,
                "is_async": self.signature.is_async,
                "is_generator": self.signature.is_generator,
                "is_abstract": self.signature.is_abstract
            },
            "is_method": self.is_method,
            "is_static": self.is_static,
            "is_class_method": self.is_class_method,
            "is_property": self.is_property,
            "is_constructor": self.is_constructor,
            "is_overridden": self.is_overridden,
            "is_override": self.is_override,
            "decorators": self.decorators,
            "calls": self.calls,
            "called_by": self.called_by,
            "semantic_traits": self.semantic_traits  # ✅ included in serialization
        })
        return result

    def _param_to_dict(self, param: ParameterSignature) -> Dict[str, Any]:
        return {
            "name": param.name,
            "type": param.type_annotation,
            "default": param.default_value,
            "is_keyword_only": param.is_keyword_only,
            "is_positional_only": param.is_positional_only,
            "is_variadic": param.is_variadic,
            "description": param.description
        }

    def generate_search_tokens(self) -> None:
        super().generate_search_tokens()
        for param in self.signature.parameters:
            self.search_tokens.add(param.name.lower())
            if param.type_annotation:
                self.search_tokens.add(param.type_annotation.lower())
        if self.signature.return_type:
            self.search_tokens.add(self.signature.return_type.lower())
        for decorator in self.decorators:
            self.search_tokens.add(decorator.lower())

    @property
    def type(self):
        return self.element_type.value if hasattr(self, "element_type") else "unknown"

    @property
    def is_module_level(self) -> bool:
        return self.parent_name is None
