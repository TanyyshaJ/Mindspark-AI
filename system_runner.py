import os
import subprocess
import time
import requests
import json

# Setup mock Git repository
def setup_mock_repo():
    os.makedirs("mock_repo", exist_ok=True)
    os.chdir("mock_repo")
    subprocess.run(["git", "init"])
    
    # Create initial files
    with open("file1.py", "w") as f:
        f.write("def function_a():\n    return 'Hello, World!'\n")
    with open("test_file1.py", "w") as f:
        f.write("def test_function_a():\n    assert function_a() == 'Hello, World!'\n")
    
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Initial commit"])
    
    # Make a change
    with open("file1.py", "a") as f:
        f.write("\ndef function_b():\n    return 'New function'\n")
    
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Add function_b"])
    
    commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    os.chdir("..")
    return os.path.abspath("mock_repo"), commit_sha

# Start Test-Sense Service
def start_test_sense_service():
    subprocess.Popen(["python", "test_sense_service.py"])
    time.sleep(5)  # Give the service time to start

# Select tests
def select_tests(repo_path, commit_sha):
    response = requests.post("http://localhost:8000/select_tests", 
                             json={"repo_path": repo_path, "commit_sha": commit_sha})
    return response.json()

# Run tests
def run_tests(selected_tests):
    test_runner_command = ["python", "test_runner.py"] + selected_tests
    result = subprocess.run(test_runner_command, capture_output=True, text=True)
    print(result.stdout)

# Main execution
if __name__ == "__main__":
    # Setup mock repository
    repo_path, commit_sha = setup_mock_repo()
    print(f"Mock repository set up at {repo_path}")
    print(f"Latest commit: {commit_sha}")

    # Start Test-Sense Service
    start_test_sense_service()
    print("Test-Sense Service started")

    # Select tests
    test_selection = select_tests(repo_path, commit_sha)
    print("Selected tests:", test_selection['selected_tests'])
    print("Explanation:", test_selection['explanation'])

    # Run tests
    run_tests(test_selection['selected_tests'])

    print("Test-Sense system test completed")