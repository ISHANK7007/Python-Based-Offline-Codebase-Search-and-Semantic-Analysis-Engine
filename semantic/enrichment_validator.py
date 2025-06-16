# from semantic.semantic_visitors import SemanticVisitorManager
# from semantic.visitors.call_visitor import CallNodeVisitor
# from semantic.visitors.override_visitor import OverrideDetectionVisitor
# from semantic.visitors.inheritance_visitor import BaseClassDepthVisitor
# from semantic.visitors.complexity_visitor import ComplexityVisitor

# Assuming these visitors are defined locally or in semantic_indexer.py for now:
from semantic.semantic_indexer import (
    SemanticVisitorManager,
    CallNodeVisitor,
    OverrideDetectionVisitor,
    BaseClassDepthVisitor,
    ComplexityVisitor
)

class SemanticIndexer:
    def __init__(self):
        self.class_index = {}  # Class name to class element mapping
        self.element_index = {}  # ID to CodeElement mapping
        self.pending_references = []

        self.visitor_manager = SemanticVisitorManager(self)
        self.visitor_manager.register_visitor('calls', CallNodeVisitor)
        self.visitor_manager.register_visitor('override', OverrideDetectionVisitor)
        self.visitor_manager.register_visitor('base_class_depth', BaseClassDepthVisitor)
        self.visitor_manager.register_visitor('complexity', ComplexityVisitor)

    def index_element(self, element):
        self.element_index[element.id] = element
        if element.type == 'class':
            self.class_index[element.name] = element

    def initialize_relationship_properties(self, element):
        if not hasattr(element, 'calls'):
            element.calls = []
        if not hasattr(element, 'called_by'):
            element.called_by = []
        if not hasattr(element, 'semantic_traits'):
            element.semantic_traits = {}

    def process_element(self, element):
        self.index_element(element)
        self.initialize_relationship_properties(element)

        semantic_traits = self.visitor_manager.analyze_element(element)
        for trait_category, traits in semantic_traits.items():
            if trait_category != 'error' and traits:
                element.semantic_traits[trait_category] = traits

        self.establish_relationships(element)
        self.resolve_pending_relationships()
        return element

    def establish_relationships(self, element):
        if 'calls' in element.semantic_traits:
            call_targets = element.semantic_traits['calls'].get('targets', [])
            for target in call_targets:
                if isinstance(target, dict) and 'element' in target:
                    called_element = target['element']
                    if called_element not in element.calls:
                        element.calls.append(called_element)
                    if element not in called_element.called_by:
                        called_element.called_by.append(element)
                elif isinstance(target, dict):
                    self.pending_references.append((element, target))

        if 'override' in element.semantic_traits:
            override_info = element.semantic_traits['override']
            if override_info.get('is_override'):
                element.overrides = override_info.get('overrides')
                base_class_name = override_info.get('base_class')
                if base_class_name in self.class_index:
                    base_class = self.class_index[base_class_name]
                    if not hasattr(base_class, 'overridden_by'):
                        base_class.overridden_by = []
                    base_class.overridden_by.append(element)

    def resolve_pending_relationships(self):
        for source, unresolved in self.pending_references:
            if unresolved.get('type') == 'reference':
                target_id = unresolved.get('id')
                if target_id in self.element_index:
                    resolved_target = self.element_index[target_id]
                    source.calls.append(resolved_target)
                    resolved_target.called_by.append(source)
        self.pending_references.clear()
