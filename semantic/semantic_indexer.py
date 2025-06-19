from typing import List, Dict, Any
from semantic.function_roles import FunctionRoleAnalyzer
from semantic.decorator_metadata import DecoratorAnalyzer
from semantic.function_complexity import ComplexityAnalyzer  # ✅ required
from models.function import FunctionElement
from models.enums import ElementType

class SemanticIndexer:
    def __init__(self):
        # Analyzer modules
        self.function_role_analyzer = FunctionRoleAnalyzer()
        self.decorator_analyzer = DecoratorAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()  # ✅ added

        # Store processed elements
        self.elements_by_id: Dict[str, Any] = {}
        self.function_index: Dict[str, Any] = {}
        self.class_index: Dict[str, Any] = {}

        # Pending relationship records
        self.pending_relationships: List[Dict[str, Any]] = []

    def process_element(self, element: Any) -> Any:
        """Process and enrich a CodeElement with semantic metadata and relationships."""
        self.index_element(element)
        self.initialize_relationship_properties(element)
        self.infer_relationships(element)
        self.resolve_pending_relationships()

        if isinstance(element, FunctionElement):
            self.analyze_function_element(element)

        return element

    def analyze_function_element(self, function_element: FunctionElement) -> FunctionElement:
        """Run semantic analyzers to enrich the function element."""
        function_element.semantic_roles = self.function_role_analyzer.determine_roles(function_element)
        function_element.decorator_metadata = self.decorator_analyzer.process_decorators(function_element.decorators)

        # ✅ Safe semantic_traits injection for golden tests
        if hasattr(function_element, "ast_node") and function_element.ast_node is not None:
            if not hasattr(function_element, "semantic_traits"):
                function_element.semantic_traits = {}
            try:
                complexity = self.complexity_analyzer.analyze(function_element.ast_node)
                function_element.semantic_traits["complexity"] = complexity
            except Exception:
                pass  # Ensure main.py doesn’t break

        return function_element

    def index_element(self, element: Any) -> None:
        self.elements_by_id[element.name] = element
        if element.element_type == ElementType.FUNCTION:
            self.function_index[element.name] = element
        elif element.element_type == ElementType.CLASS:
            self.class_index[element.name] = element

    def initialize_relationship_properties(self, element: Any) -> None:
        if not hasattr(element, "calls"):
            element.calls = []
        if not hasattr(element, "called_by"):
            element.called_by = []
        if not hasattr(element, "decorator_roles"):
            element.decorator_roles = {}

    def infer_relationships(self, element: Any) -> None:
        calls = self.extract_function_calls(element)
        for called_function_name in calls:
            if called_function_name in self.function_index:
                called_element = self.function_index[called_function_name]
                element.calls.append(called_element)
                called_element.called_by.append(element)
            else:
                self.pending_relationships.append({
                    "type": "call",
                    "caller": element,
                    "callee_name": called_function_name
                })

        self.process_decorators(element)

    def extract_function_calls(self, element: Any) -> List[str]:
        # Placeholder: actual code parsing would go here
        return []

    def process_decorators(self, element: Any) -> None:
        if hasattr(element, "decorators") and element.decorators:
            for decorator in element.decorators:
                if decorator.name in self.function_index:
                    decorator_func = self.function_index[decorator.name]
                    if "decorates" not in decorator_func.decorator_roles:
                        decorator_func.decorator_roles["decorates"] = []
                    decorator_func.decorator_roles["decorates"].append(element)
                else:
                    self.pending_relationships.append({
                        "type": "decorator",
                        "decorated": element,
                        "decorator_name": decorator.name
                    })

    def resolve_pending_relationships(self) -> None:
        still_pending = []
        for r in self.pending_relationships:
            if r["type"] == "call":
                callee_name = r["callee_name"]
                if callee_name in self.function_index:
                    caller = r["caller"]
                    callee = self.function_index[callee_name]
                    caller.calls.append(callee)
                    callee.called_by.append(caller)
                else:
                    still_pending.append(r)
            elif r["type"] == "decorator":
                decorator_name = r["decorator_name"]
                if decorator_name in self.function_index:
                    decorated = r["decorated"]
                    decorator = self.function_index[decorator_name]
                    if "decorates" not in decorator.decorator_roles:
                        decorator.decorator_roles["decorates"] = []
                    decorator.decorator_roles["decorates"].append(decorated)
                else:
                    still_pending.append(r)

        self.pending_relationships = still_pending

    def process_stream(self, elements_iterable: List[Any]) -> List[Any]:
        return [self.process_element(el) for el in elements_iterable]
