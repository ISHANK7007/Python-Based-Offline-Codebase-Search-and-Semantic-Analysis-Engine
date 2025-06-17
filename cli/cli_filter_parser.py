from index.query.field_filter import FieldFilter
from index.query.filters import AndFilter, OrFilter, NotFilter
from index.query.matching_strategies import (
    ExactMatchingStrategy,
    StartsWithStrategy,
    RegexStrategy,
    FuzzyStrategy
)
from index.query.semantic_filters import DecoratorFilter, RoleFilter
from index.query.relationship_filter import RelationshipFilter  # Assuming this exists
from index.query.includes_strategy import IncludesStrategy      # Assuming this exists

def build_filter_from_args(args):
    """Build a composite filter expression from CLI arguments"""
    filters = []

    # Field filters with default exact strategy
    if getattr(args, 'name', None):
        filters.append(FieldFilter('name', args.name, strategy=ExactMatchingStrategy()))
    if getattr(args, 'path', None):
        filters.append(FieldFilter('file_path', args.path, strategy=ExactMatchingStrategy()))
    if getattr(args, 'role', None):
        filters.append(FieldFilter('role', args.role, strategy=ExactMatchingStrategy()))
    if getattr(args, 'type', None):
        filters.append(FieldFilter('type', args.type, strategy=ExactMatchingStrategy()))
    if getattr(args, 'decorator', None):
        filters.append(FieldFilter('decorator', args.decorator, strategy=ExactMatchingStrategy()))
    if getattr(args, 'doc', None):
        filters.append(FieldFilter('doc', args.doc, strategy=ExactMatchingStrategy()))

    # Field filters with advanced strategies
    if getattr(args, 'name_startswith', None):
        filters.append(FieldFilter('name', args.name_startswith, strategy=StartsWithStrategy()))
    if getattr(args, 'name_regex', None):
        filters.append(FieldFilter('name', args.name_regex, strategy=RegexStrategy()))
    if getattr(args, 'name_fuzzy', None):
        threshold = getattr(args, 'threshold', 0.7)
        filters.append(FieldFilter('name', args.name_fuzzy, strategy=FuzzyStrategy(threshold=threshold)))
    if getattr(args, 'doc_includes', None):
        filters.append(FieldFilter('doc', args.doc_includes, strategy=IncludesStrategy()))

    # Multi-field OR filters for --contains
    if getattr(args, 'contains', None):
        fields = args.fields.split(',') if getattr(args, 'fields', None) else ['name', 'doc', 'file_path']
        or_filters = [
            FieldFilter(field, args.contains, strategy=IncludesStrategy())
            for field in fields
        ]
        if or_filters:
            filters.append(OrFilter(or_filters))

    # Relationship filters
    if getattr(args, 'calls', None):
        filters.append(RelationshipFilter('calls', args.calls))
    if getattr(args, 'called_by', None):
        filters.append(RelationshipFilter('called_by', args.called_by))
    if getattr(args, 'inherits', None):
        filters.append(RelationshipFilter('inherits', args.inherits))
    if getattr(args, 'imported_by', None):
        filters.append(RelationshipFilter('imported_by', args.imported_by))

    # No filters? Return None
    if not filters:
        return None

    # Combine using OR if --any, otherwise AND (default)
    combined = OrFilter(filters) if getattr(args, 'any', False) else AndFilter(filters)

    # Apply NOT if --not is set
    if getattr(args, 'not', False):
        combined = NotFilter(combined)

    return combined
