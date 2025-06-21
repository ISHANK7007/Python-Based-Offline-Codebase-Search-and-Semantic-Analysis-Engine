
import unittest
from models.semantic_nodes import ClassElement
from semantic.semantic_indexer import SemanticIndexer

class TestSemanticEnrichment(unittest.TestCase):
    def setUp(self):
        self.indexer = SemanticIndexer()

        # Define mock classes for inheritance
        self.base_class = ClassElement(id="1", name="BaseClass", type="class", base_classes=[])
        self.mid_class = ClassElement(id="2", name="MidClass", type="class", base_classes=["BaseClass"])
        self.sub_class = ClassElement(id="3", name="SubClass", type="class", base_classes=["MidClass"])

        # Inject base classes into index
        self.indexer.class_index["BaseClass"] = self.base_class
        self.indexer.class_index["MidClass"] = self.mid_class

    def test_inheritance_depth_and_path(self):
        # Enrich sub_class with semantic traits
        enriched = self.indexer.process_element(self.sub_class)
        traits = enriched.semantic_traits.get('base_class_depth', {})

        self.assertEqual(traits.get('base_class_depth'), 2)
        self.assertEqual(traits.get('inheritance_path'), ["SubClass", "MidClass", "BaseClass"])

        print("Inheritance Depth:", traits.get('base_class_depth'))
        print("Inheritance Path:", " -> ".join(traits.get('inheritance_path')))

if __name__ == "__main__":
    unittest.main()
