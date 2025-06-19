# cli/utils/pager.py
class Pager:
    def __init__(self, prefer_system_pager=True, page_threshold=20):
        self.prefer_system_pager = prefer_system_pager
        self.page_threshold = page_threshold

    def page(self, text: str):
        print(text)  # You can use pydoc.pager or subprocess for actual paging

    def page_to_temp_file(self, text: str, syntax: str = None):
        self.page(text)  # Simplified fallback
