
from semantic.semantic_indexer import SemanticIndexer

# Simulated stream of elements (replace with actual stream or list)
code_elements_stream = []  # Replace with real elements

# Create semantic indexer
indexer = SemanticIndexer()

# Process each code element and augment with semantic relationships
for code_element in code_elements_stream:
    enriched_element = indexer.process_element(code_element)

    print(f"\n🔍 Element: {enriched_element.name}")

    # Print call relationships
    calls = getattr(enriched_element, 'calls', [])
    called_by = getattr(enriched_element, 'called_by', [])
    decorator_roles = getattr(enriched_element, 'decorator_roles', [])

    print(f"  ➤ Calls: {[e.name for e in calls]}")
    print(f"  ➤ Called by: {[e.name for e in called_by]}")
    print(f"  ➤ Decorator roles: {decorator_roles}")
