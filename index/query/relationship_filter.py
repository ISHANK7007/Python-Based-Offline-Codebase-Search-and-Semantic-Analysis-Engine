# index/query/relationship_filter.py

from index.query.filters import Filter

class RelationshipFilter(Filter):
    def __init__(self, relation_type, target_name):
        self.relation_type = relation_type
        self.target_name = target_name

    def matches(self, item):
        if not hasattr(item, self.relation_type):
            return False
        related = getattr(item, self.relation_type, [])
        return self.target_name in related
