@DiffStrategyRegistry.register
class CodeBERTDiffStrategy(MLSemanticDiffStrategy):
    """Use CodeBERT for code understanding and diffing."""
    
    def __init__(self, model_path=None):
        """Initialize CodeBERT model."""
        try:
            from transformers import AutoModel, AutoTokenizer
            
            model_name = model_path or "microsoft/codebert-base"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
        except ImportError:
            raise ImportError("This strategy requires transformers library")
    
    def _get_code_embedding(self, element):
        """Generate embedding using CodeBERT."""
        import torch
        
        code = element.get_source()
        inputs = self.tokenizer(code, return_tensors="pt", 
                               truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Use [CLS] token embedding as code representation
        return outputs.last_hidden_state[:, 0, :].squeeze().numpy()