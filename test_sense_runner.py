import sys
import requests
import json
import subprocess

def run_test_sense_pipeline(repo_path, commit_sha):
    # Step 1: Select tests
    response = requests.post("http://localhost:8000/select_tests", 
                             json={"repo_path": repo_path, "commit_sha": commit_sha})
    if response.status_code != 200:
        print(f"Failed to select tests: {response.text}")
        sys.exit(1)
    
    test_selection = response.json()
    selected_tests = test_selection['selected_tests']
    explanation = test_selection['explanation']
    
    print("Selected tests:", selected_tests)
    print("Explanation:", explanation)
    
    # Step 2: Run tests
    test_runner_command = ["python", "test_runner.py"] + selected_tests
    result = subprocess.run(test_runner_command, capture_output=True, text=True)
    
    print("Test execution output:")
    print(result.stdout)
    
    # Step 3: Update call graph
    call_graph = json.loads(result.stdout)
    response = requests.post("http://localhost:8000/update_call_graph", json=call_graph)
    if response.status_code != 200:
        print(f"Failed to update call graph: {response.text}")
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump({
            "selected_tests": selected_tests,
            "explanation": explanation,
            "test_output": result.stdout,
            "call_graph": call_graph
        }, f)

if __name__ == "__main__":
    repo_path = sys.argv[1]
    commit_sha = sys.argv[2]
    run_test_sense_pipeline(repo_path, commit_sha)