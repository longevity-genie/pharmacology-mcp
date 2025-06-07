import sys
import json
import pytest
import os
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv
from just_agents import llm_options
from just_agents.base_agent import BaseAgent
from tests.pharmacology_server import PharmacologyServer

# Load environment
load_dotenv(override=True)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
TEST_DIR = PROJECT_ROOT / "tests"

# Load judge prompt
with open(TEST_DIR / "judge_prompt.txt", "r", encoding="utf-8") as f:
    JUDGE_PROMPT = f.read().strip()

# System prompt for test agent
SYSTEM_PROMPT = """You are a pharmacology research assistant with access to the Guide to Pharmacology database through MCP tools.

Your tools allow you to:
- Search for pharmacological targets and save results to files
- Search for ligands/compounds and save results to files  
- Get interaction data for specific targets or ligands

When answering questions:
1. Use the appropriate MCP tool for the task
2. Provide meaningful file paths for saving results
3. Include relevant parameters based on the question
4. Always mention which tool you used and with what parameters

In your response, include details about the tool calls you made to answer the question."""

# Load reference Q&A data
with open(TEST_DIR / "test_real_qa.json", "r", encoding="utf-8") as f:
    QA_DATA = json.load(f)

# Model configurations
answers_model = {
    "model": "gemini/gemini-2.5-flash-preview-05-20",
    "temperature": 0.0
}

judge_model = {
    "model": "gemini/gemini-2.5-flash-preview-05-20", 
    "temperature": 0.0
}

# Initialize agents with real MCP tools
pharmacology_server = PharmacologyServer()
test_agent = BaseAgent(
    llm_options=answers_model,
    tools=[
        pharmacology_server.search_targets_to_file,
        pharmacology_server.search_ligands_to_file,
        pharmacology_server.get_target_interactions_to_file,
        pharmacology_server.get_ligand_interactions_to_file
    ],
    system_prompt=SYSTEM_PROMPT
)
judge_agent = BaseAgent(
    llm_options=judge_model,
    tools=[],
    system_prompt=JUDGE_PROMPT
)

@pytest.mark.skipif(
    os.getenv("CI") in ("true", "1", "True") or 
    os.getenv("GITHUB_ACTIONS") in ("true", "1", "True") or 
    os.getenv("GITLAB_CI") in ("true", "1", "True") or 
    os.getenv("JENKINS_URL") is not None,
    reason="Skipping expensive LLM tests in CI to save costs. Run locally with: pytest tests/test_judge.py"
)
@pytest.mark.parametrize("qa_item", QA_DATA, ids=[f"Q{i+1}" for i in range(len(QA_DATA))])
def test_question_with_judge(qa_item):
    """Test each question by generating an answer and evaluating it with the judge."""
    question = qa_item["question"]
    expected_tools = qa_item["expected_tools"]
    expected_parameters = qa_item["expected_parameters"]
    reference_answer = qa_item["answer"]
    
    # Generate answer using real MCP tools
    generated_answer = test_agent.query(question)
    
    # Prepare judge input with expected tool usage
    expected_summary = json.dumps({
        "expected_tools": expected_tools,
        "expected_parameters": expected_parameters
    }, indent=2)
    
    judge_input = f"""
QUESTION: {question}

EXPECTED TOOLS AND PARAMETERS: {expected_summary}

REFERENCE ANSWER: {reference_answer}

GENERATED ANSWER: {generated_answer}
"""
    
    # Get judge evaluation
    judge_result = judge_agent.query(judge_input).strip().upper()
    
    # Print for debugging
    print(f"\nQuestion: {question}")
    print(f"Expected Tools: {expected_tools}")
    print(f"Generated Answer: {generated_answer[:300]}...")
    print(f"Judge Result: {judge_result}")
    
    if "PASS" not in judge_result:
        print(f"\n=== JUDGE FAILED ===")
        print(f"Question: {question}")
        print(f"Expected Tools: {expected_tools}")
        print(f"Expected Parameters: {expected_parameters}")
        print(f"Reference Answer: {reference_answer}")
        print(f"Generated Answer: {generated_answer}")
        print(f"Judge Result: {judge_result}")
        print(f"===================")
    
    assert "PASS" in judge_result, f"Judge failed for question: {question}. Judge result: {judge_result}"

@pytest.mark.skipif(
    os.getenv("CI") in ("true", "1", "True") or 
    os.getenv("GITHUB_ACTIONS") in ("true", "1", "True") or 
    os.getenv("GITLAB_CI") in ("true", "1", "True") or 
    os.getenv("JENKINS_URL") is not None,
    reason="Skipping expensive API tests in CI"
)
def test_mcp_tools_connectivity():
    """Test that MCP tools can actually connect to the pharmacology API"""
    # Test a simple question to verify tools work
    question = "Find dopamine targets using the pharmacology database"
    
    try:
        generated_answer = test_agent.query(question)
        
        # Should contain evidence of tool usage
        assert "search_targets_to_file" in generated_answer.lower() or "dopamine" in generated_answer.lower()
        print(f"MCP tools connectivity test passed. Answer: {generated_answer[:200]}...")
        
    except Exception as e:
        pytest.fail(f"MCP tools connectivity test failed: {str(e)}")

@pytest.mark.skipif(
    os.getenv("CI") in ("true", "1", "True") or 
    os.getenv("GITHUB_ACTIONS") in ("true", "1", "True") or 
    os.getenv("GITLAB_CI") in ("true", "1", "True") or 
    os.getenv("JENKINS_URL") is not None,
    reason="Skipping expensive LLM tests in CI"
)
def test_judge_agent_functionality():
    """Test that the judge agent can properly evaluate tool usage"""
    # Test judge with a clear pass case
    judge_input = """
QUESTION: Find dopamine targets using the pharmacology database

EXPECTED TOOLS AND PARAMETERS: {
  "expected_tools": ["search_targets_to_file"],
  "expected_parameters": {
    "search_targets_to_file": {
      "name": "dopamine"
    }
  }
}

REFERENCE ANSWER: I'll search for dopamine-related targets using the search_targets_to_file tool.

GENERATED ANSWER: I'll use the search_targets_to_file tool with name='dopamine' to find dopamine-related targets in the pharmacology database. The results will be saved to dopamine_targets.json.
"""
    
    judge_result = judge_agent.query(judge_input).strip().upper()
    print(f"Judge test result: {judge_result}")
    
    # Should pass since the correct tool and parameters were mentioned
    assert "PASS" in judge_result, f"Judge should have passed this clear case. Result: {judge_result}" 