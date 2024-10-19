import os

def setup_mock_repo():
    os.makedirs("mock_repo", exist_ok=True)
    os.chdir("mock_repo")
    subprocess.run(["git", "init"])
    
    # Create initial files
    with open("math_operations.py", "w") as f:
        f.write("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b
""")
    
    with open("test_math_operations.py", "w") as f:
        f.write("""
import unittest
from math_operations import add, subtract, multiply

class TestMathOperations(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
    
    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
    
    def test_multiply(self):
        self.assertEqual(multiply(2, 3), 6)
""")
    
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Initial commit"])
    
    # Make a change that should only affect the add function
    with open("math_operations.py", "a") as f:
        f.write("""
def add(a, b):
    return a + b + 1  # Intentional bug
""")
    
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Modify add function"])
    
    commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    os.chdir("..")
    return os.path.abspath("mock_repo"), commit_sha