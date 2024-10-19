import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class AITestPredictor:
    def __init__(self, model_name="microsoft/codebert-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.function_embeddings = {}
        self.test_embeddings = {}

    def _get_embedding(self, code):
        inputs = self.tokenizer(code, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def add_function(self, function_name, function_code):
        self.function_embeddings[function_name] = self._get_embedding(function_code)

    def add_test(self, test_name, test_code):
        self.test_embeddings[test_name] = self._get_embedding(test_code)

    def predict_impacted_tests(self, changed_functions, threshold=0.5):
        impacted_tests = []
        for func_name in changed_functions:
            if func_name in self.function_embeddings:
                func_embedding = self.function_embeddings[func_name]
                for test_name, test_embedding in self.test_embeddings.items():
                    similarity = cosine_similarity(func_embedding, test_embedding)[0][0]
                    if similarity > threshold:
                        impacted_tests.append((test_name, similarity))
        
        return sorted(impacted_tests, key=lambda x: x[1], reverse=True)

# Usage
predictor = AITestPredictor()

# Add functions and tests
predictor.add_function("function_a", "def function_a():\n    print('Hello, World!')")
predictor.add_test("test_function_a", "def test_function_a():\n    assert function_a() == 'Hello, World!'")

# Predict impacted tests
changed_functions = ["function_a"]
impacted_tests = predictor.predict_impacted_tests(changed_functions)
print(f"Impacted tests: {impacted_tests}")