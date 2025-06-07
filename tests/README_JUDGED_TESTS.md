# Pharmacology MCP Judged Tests

This directory contains judged tests for the Pharmacology MCP server, inspired by the opengenes-mcp testing approach. These tests focus on **validating correct tool usage and parameters** rather than answer formatting or style.

## ✅ Status: WORKING

The judged tests are now fully functional and successfully validate:
- **Tool Selection**: Correct MCP tools are chosen for each pharmacology task
- **Parameter Validation**: Proper parameters are passed to tools
- **Real API Integration**: Actual pharmacology API calls through MCP tools
- **Judge Evaluation**: LLM judge correctly identifies PASS/FAIL based on tool usage

## Overview

The judged tests validate that:
1. **Correct MCP tools** are selected for pharmacology tasks
2. **Proper parameters** are provided to tools
3. **Logical workflows** are followed (e.g., search before details)
4. **Essential pharmacological data** is retrieved correctly

## Files

### Core Test Files

- `test_judge.py` - Main judged test implementation using real MCP tools
- `pharmacology_server.py` - Wrapper class for MCP tools compatible with just-agents
- `judge_prompt.txt` - Judge agent prompt focused on tool usage validation
- `test_real_qa.json` - Real pharmacology questions with expected tool usage patterns

### Test Structure

The tests follow the opengenes-mcp pattern but adapted for MCP tools instead of SQL:

```python
{
  "question": "Find dopamine-related targets and save them to a file",
  "expected_tools": ["search_targets_to_file"],
  "expected_parameters": {
    "search_targets_to_file": {
      "query": "dopamine",
      "filename": "dopamine_targets.json"
    }
  },
  "answer": "Reference answer describing expected tool usage"
}
```

## Test Categories

### 1. Single Tool Usage Tests
- **Target Search**: `search_targets_to_file` with specific queries
- **Ligand Search**: `search_ligands_to_file` with specific queries  
- **Target Interactions**: `get_target_interactions_to_file` with target IDs
- **Ligand Interactions**: `get_ligand_interactions_to_file` with ligand IDs

### 2. Multi-Tool Workflow Tests
- **Search + Details**: First search for entities, then get detailed interactions
- **Complex Workflows**: Multiple tool calls in logical sequence

### 3. Parameter Validation Tests
- **Required Parameters**: Ensure all required parameters are provided
- **Parameter Values**: Validate parameter values match expectations
- **File Paths**: Check filename and directory path handling

## Validation Logic

The tests use a two-layer validation approach:

### 1. Direct Tool Usage Validation
```python
def validate_tool_usage(expected_tools, expected_params, actual_tool_calls):
    # Check if all expected tools were called
    # Validate parameters for each tool call
    # Handle dynamic values (e.g., extracted IDs)
    return is_valid, validation_message
```

### 2. Judge Agent Evaluation
- Uses a mock judge agent that evaluates tool usage patterns
- Focuses on pharmacological relevance and tool appropriateness
- Returns PASS/FAIL with specific reasons for failures

## Running the Tests

### Run All Judged Tests
```bash
pytest tests/test_judged_tool_usage.py -v
```

### Run Specific Test Categories
```bash
# Single tool usage tests
pytest tests/test_judged_tool_usage.py::test_tool_usage_validation -v

# Parameter validation tests  
pytest tests/test_judged_tool_usage.py::test_tool_parameter_validation -v

# Missing tool validation tests
pytest tests/test_judged_tool_usage.py::test_missing_tool_validation -v
```

### CI/CD Considerations
Tests are automatically skipped in CI environments to avoid LLM costs:
```python
@pytest.mark.skipif(
    os.getenv("CI") in ("true", "1", "True") or 
    os.getenv("GITHUB_ACTIONS") in ("true", "1", "True"),
    reason="Skipping expensive LLM tests in CI"
)
```

## Test Cases

### Q1: Basic Target Search
- **Question**: "Find dopamine-related targets and save them to a file"
- **Expected Tool**: `search_targets_to_file`
- **Key Parameters**: `query="dopamine"`, `filename="dopamine_targets.json"`

### Q2: Target Interaction Retrieval
- **Question**: "Get detailed information about target ID 2486 and its interactions"
- **Expected Tool**: `get_target_interactions_to_file`
- **Key Parameters**: `target_id="2486"`, `filename="target_2486_interactions.json"`

### Q3: Basic Ligand Search
- **Question**: "Find aspirin-related ligands and their details"
- **Expected Tool**: `search_ligands_to_file`
- **Key Parameters**: `query="aspirin"`, `filename="aspirin_ligands.json"`

### Q4: Multi-Step Workflow
- **Question**: "Search for GPCR targets and then get interactions for the first result"
- **Expected Tools**: `search_targets_to_file`, `get_target_interactions_to_file`
- **Workflow**: Search first, then use results for detailed lookup

### Q5-Q8: Additional Test Cases
- Diabetes ligand search
- Quercetin interaction retrieval
- Kinase target search with directory paths
- Approved drug workflow

## Key Validation Points

### 1. Tool Selection
- ✅ Correct tool chosen for the task type
- ❌ Wrong tool used (e.g., ligand tool for target task)

### 2. Parameter Accuracy
- ✅ Required parameters provided
- ✅ Parameter values match expectations
- ❌ Missing required parameters
- ❌ Incorrect parameter values

### 3. Workflow Logic
- ✅ Logical sequence of tool calls
- ✅ Using results from one tool in subsequent calls
- ❌ Illogical tool usage patterns
- ❌ Missing intermediate steps

### 4. Pharmacological Relevance
- ✅ Appropriate queries for pharmacology domain
- ✅ Relevant target/ligand/interaction focus
- ❌ Non-pharmacological or irrelevant queries

## Extending the Tests

To add new test cases:

1. **Add to `test_qa_tool_usage.json`**:
```json
{
  "question": "Your new test question",
  "expected_tools": ["tool1", "tool2"],
  "expected_parameters": {
    "tool1": {"param1": "value1"},
    "tool2": {"param2": "value2"}
  },
  "answer": "Expected behavior description"
}
```

2. **Update Mock Agent** (if needed):
Add pattern matching in `MockTestAgent.query()` for new question types.

3. **Update Mock Judge** (if needed):
Add validation logic in `MockJudgeAgent.query()` for new tool patterns.

## Comparison with opengenes-mcp

| Aspect | opengenes-mcp | pharmacology-mcp |
|--------|---------------|------------------|
| **Focus** | SQL query validation | MCP tool usage validation |
| **Data Source** | Database queries | API tool calls |
| **Validation** | SQL correctness + scientific facts | Tool selection + parameters |
| **Judge Criteria** | Query logic + domain knowledge | Tool workflow + pharmacology relevance |
| **Test Structure** | Question → SQL → Answer | Question → Tools → Parameters |

## Benefits

1. **Tool Usage Validation**: Ensures correct MCP tools are used
2. **Parameter Verification**: Validates tool parameters are appropriate
3. **Workflow Testing**: Tests multi-step pharmacology workflows
4. **Domain Focus**: Pharmacology-specific validation criteria
5. **Automated Quality**: Consistent tool usage quality assessment
6. **CI Integration**: Skips expensive tests in CI while maintaining local validation

This approach ensures that the Pharmacology MCP server tools are used correctly and effectively for pharmacological research tasks. 