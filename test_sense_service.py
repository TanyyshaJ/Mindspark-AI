import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from git import Repo
import networkx as nx
from transformers import AutoTokenizer, AutoModel
import torch
import subprocess

app = FastAPI()

class GitInfo(BaseModel):
    repo_path: str
    commit_sha: str

class TestSelection(BaseModel):
    selected_tests: list
    explanation: str

class CallGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_edge(self, caller, callee):
        self.graph.add_edge(caller, callee)

    def get_impacted_functions(self, changed_functions):
        impacted = set(changed_functions)
        for func in changed_functions:
            impacted.update(nx.descendants(self.graph, func))
        return list(impacted)

call_graph = CallGraph()

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

def analyze_git_diff(repo_path, commit_sha):
    repo = Repo(repo_path)
    commit = repo.commit(commit_sha)
    diff = commit.diff(commit.parents[0])
    changed_files = [d.a_path for d in diff]
    return changed_files

def extract_functions(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    # This is a simplified function extraction. In a real-world scenario,
    # you'd use a proper parser for the specific language.
    functions = [line.strip() for line in content.split('\n') if line.strip().startswith('def ')]
    return functions

def predict_impacted_tests(changed_functions):
    inputs = tokenizer(changed_functions, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # This is a simplified prediction. In a real-world scenario,
    # you'd have a more sophisticated model and prediction logic.
    embeddings = outputs.last_hidden_state.mean(dim=1)
    similarity = torch.matmul(embeddings, embeddings.T)
    return [f"test_{func}" for func, sim in zip(changed_functions, similarity.diag()) if sim > 0.5]

@app.post("/select_tests")
async def select_tests(git_info: GitInfo):
    changed_files = analyze_git_diff(git_info.repo_path, git_info.commit_sha)
    changed_functions = []
    for file in changed_files:
        changed_functions.extend(extract_functions(os.path.join(git_info.repo_path, file)))
    
    impacted_functions = call_graph.get_impacted_functions(changed_functions)
    ai_predicted_tests = predict_impacted_tests(impacted_functions)
    
    all_tests = set(ai_predicted_tests + [f"test_{func}" for func in impacted_functions])
    
    explanation = f"Selected {len(all_tests)} tests based on {len(changed_files)} changed files and {len(impacted_functions)} impacted functions."
    
    return TestSelection(selected_tests=list(all_tests), explanation=explanation)

@app.post("/update_call_graph")
async def update_call_graph(test_results: dict):
    for test, calls in test_results.items():
        for caller, callee in calls:
            call_graph.add_edge(caller, callee)
    return {"status": "Call graph updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)