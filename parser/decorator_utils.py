
from semantic.semantic_indexer import SemanticIndexer
from models.semantic_nodes import ClassElement, FunctionElement

# Create indexer with visitor framework
indexer = SemanticIndexer()

# Process a class element
class_element = ClassElement(
    id="class1", 
    name="MyClass", 
    type="class", 
    definition="class MyClass(BaseClass):\n    pass"
)
processed_class = indexer.process_element(class_element)

# Check semantic traits
if 'base_class_depth' in processed_class.semantic_traits:
    base_depth = processed_class.semantic_traits['base_class_depth'].get('base_class_depth')
    inheritance_path = processed_class.semantic_traits['base_class_depth'].get('inheritance_path', [])
    print(f"Class {processed_class.name} has inheritance depth {base_depth}")
    print(f"Inheritance path: {' -> '.join(inheritance_path)}")
else:
    print("No base class depth information available.")

# Process a function element
function_element = FunctionElement(
    id="func1", 
    name="process_data", 
    type="function", 
    body="""def process_data(data):
    if data:
        for item in data:
            if item.valid:
                process_item(item)
    return data"""
)
processed_function = indexer.process_element(function_element)

# Check complexity metrics
if 'complexity' in processed_function.semantic_traits:
    complexity = processed_function.semantic_traits['complexity']
    print(f"Function {processed_function.name} complexity: {complexity.get('cyclomatic_complexity')}")
    if complexity.get('is_complex'):
        print("This function is too complex and should be refactored.")
else:
    print("No complexity metrics available.")
