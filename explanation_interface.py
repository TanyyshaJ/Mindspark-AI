from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class TestSelectionExplanation(BaseModel):
    changed_files: list
    changed_functions: list
    impacted_functions: list
    ai_predicted_tests: list
    selected_tests: list

class ExplanationInterface:
    @staticmethod
    def generate_explanation(explanation_data: TestSelectionExplanation):
        explanation = []
        explanation.append(f"Changed files: {', '.join(explanation_data.changed_files)}")
        explanation.append(f"Changed functions: {', '.join(explanation_data.changed_functions)}")
        explanation.append(f"Impacted functions: {', '.join(explanation_data.impacted_functions)}")
        explanation.append(f"AI-predicted tests: {', '.join([test for test, _ in explanation_data.ai_predicted_tests])}")
        explanation.append(f"Final selected tests: {', '.join(explanation_data.selected_tests)}")
        
        return "\n".join(explanation)

@app.post("/explain_test_selection")
async def explain_test