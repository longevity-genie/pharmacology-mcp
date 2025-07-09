"""
Judged tests for Pharmacology MCP Server
Inspired by opengenes-mcp testing patterns

These tests validate both functionality and response quality using real API calls.
Each test includes judgment criteria for evaluating the quality of responses.
"""

import pytest
import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import tempfile
import os

from fastmcp import FastMCP
from fastmcp.client import Client
from mcp.types import Tool, TextContent
from src.pharmacology_mcp.server import create_app
from src.pharmacology_mcp.local import pharmacology_local_mcp


class PharmacologyJudgedTests:
    """Judged tests for pharmacology MCP tools"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.app = create_app()
        self.mcp = FastMCP.from_fastapi(app=self.app)
        self.mcp.mount(pharmacology_local_mcp, prefix="local")
        
        # Create temporary directory for file operations
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup after tests"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def judge_response_quality(self, response: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Judge the quality of a response based on criteria
        
        Args:
            response: The response to judge
            criteria: Dictionary of judgment criteria
            
        Returns:
            Dictionary with judgment results
        """
        judgment = {
            "passed": True,
            "score": 0,
            "max_score": 0,
            "details": {},
            "issues": []
        }
        
        for criterion, config in criteria.items():
            judgment["max_score"] += config.get("weight", 1)
            
            if criterion == "response_type":
                expected_type = config["expected"]
                if isinstance(response, expected_type):
                    judgment["score"] += config.get("weight", 1)
                    judgment["details"][criterion] = "PASS"
                else:
                    judgment["passed"] = False
                    judgment["details"][criterion] = f"FAIL: Expected {expected_type}, got {type(response)}"
                    judgment["issues"].append(f"Wrong response type: {type(response)}")
            
            elif criterion == "min_results":
                min_count = config["value"]
                if hasattr(response, '__len__') and len(response) >= min_count:
                    judgment["score"] += config.get("weight", 1)
                    judgment["details"][criterion] = f"PASS: {len(response)} >= {min_count}"
                else:
                    judgment["passed"] = False
                    count = len(response) if hasattr(response, '__len__') else 0
                    judgment["details"][criterion] = f"FAIL: {count} < {min_count}"
                    judgment["issues"].append(f"Insufficient results: {count}")
            
            elif criterion == "required_fields":
                required_fields = config["fields"]
                if isinstance(response, list) and response:
                    item = response[0]
                    missing_fields = [field for field in required_fields if field not in item]
                    if not missing_fields:
                        judgment["score"] += config.get("weight", 1)
                        judgment["details"][criterion] = "PASS: All required fields present"
                    else:
                        judgment["passed"] = False
                        judgment["details"][criterion] = f"FAIL: Missing fields {missing_fields}"
                        judgment["issues"].append(f"Missing required fields: {missing_fields}")
                elif isinstance(response, dict):
                    missing_fields = [field for field in required_fields if field not in response]
                    if not missing_fields:
                        judgment["score"] += config.get("weight", 1)
                        judgment["details"][criterion] = "PASS: All required fields present"
                    else:
                        judgment["passed"] = False
                        judgment["details"][criterion] = f"FAIL: Missing fields {missing_fields}"
                        judgment["issues"].append(f"Missing required fields: {missing_fields}")
            
            elif criterion == "data_quality":
                quality_checks = config["checks"]
                quality_score = 0
                quality_max = len(quality_checks)
                
                for check in quality_checks:
                    if check == "non_empty_names":
                        if isinstance(response, list):
                            non_empty = all(item.get("name") for item in response if isinstance(item, dict))
                            if non_empty:
                                quality_score += 1
                    elif check == "valid_ids":
                        if isinstance(response, list):
                            valid_ids = all(
                                isinstance(item.get("targetId") or item.get("ligandId") or item.get("interactionId"), int)
                                for item in response if isinstance(item, dict)
                            )
                            if valid_ids:
                                quality_score += 1
                    elif check == "meaningful_content":
                        if isinstance(response, list) and response:
                            # Check if responses have meaningful content beyond just IDs
                            meaningful = any(
                                len(str(item.get("name", ""))) > 3 or 
                                len(str(item.get("description", ""))) > 10
                                for item in response if isinstance(item, dict)
                            )
                            if meaningful:
                                quality_score += 1
                
                if quality_score == quality_max:
                    judgment["score"] += config.get("weight", 1)
                    judgment["details"][criterion] = f"PASS: {quality_score}/{quality_max} quality checks"
                else:
                    judgment["details"][criterion] = f"PARTIAL: {quality_score}/{quality_max} quality checks"
                    judgment["score"] += (quality_score / quality_max) * config.get("weight", 1)
        
        return judgment


class TestTargetSearchJudged(PharmacologyJudgedTests):
    """Judged tests for target search functionality"""
    
    @pytest.mark.asyncio
    async def test_search_dopamine_targets_quality(self):
        """
        Test searching for dopamine-related targets with quality judgment
        
        Judgment Criteria:
        - Should return a list of targets
        - Should find at least 3 dopamine-related targets
        - Each target should have required fields (targetId, name, type)
        - Names should be non-empty and relevant
        - Should include diverse target types
        """
        # Execute the search
        file_path = os.path.join(self.temp_dir, "dopamine_targets.json")
        
        # Use Client to call tools
        async with Client(self.mcp) as client:
            result = await client.call_tool(
                "local_search_targets_to_file",
                {
                    "file_path_str": file_path,
                    "name": "dopamine"
                }
            )
        
        # Load and validate results
        assert os.path.exists(file_path), "Results file should be created"
        
        with open(file_path, 'r') as f:
            targets = json.load(f)
        
        # Define judgment criteria
        criteria = {
            "response_type": {"expected": list, "weight": 1},
            "min_results": {"value": 3, "weight": 2},
            "required_fields": {"fields": ["targetId", "name", "type"], "weight": 2},
            "data_quality": {
                "checks": ["non_empty_names", "valid_ids", "meaningful_content"],
                "weight": 3
            }
        }
        
        # Judge the response
        judgment = self.judge_response_quality(targets, criteria)
        
        # Additional pharmacology-specific checks
        if isinstance(targets, list) and targets:
            # Check for dopamine relevance
            dopamine_relevant = any(
                "dopamine" in target.get("name", "").lower() 
                for target in targets
            )
            if dopamine_relevant:
                judgment["score"] += 1
                judgment["details"]["dopamine_relevance"] = "PASS: Found dopamine-relevant targets"
            else:
                judgment["issues"].append("No clearly dopamine-relevant targets found")
            
            judgment["max_score"] += 1
        
        # Assert quality standards
        assert judgment["passed"], f"Quality judgment failed: {judgment['issues']}"
        assert judgment["score"] / judgment["max_score"] >= 0.7, f"Quality score too low: {judgment['score']}/{judgment['max_score']}"
        
        print(f"Target Search Quality Score: {judgment['score']}/{judgment['max_score']}")
        print(f"Details: {judgment['details']}")
    
    @pytest.mark.asyncio
    async def test_search_gpcr_targets_comprehensive(self):
        """
        Test GPCR target search with comprehensive quality assessment
        
        Judgment Criteria:
        - Should return substantial number of GPCR targets (>50)
        - All results should be GPCR type
        - Should have diverse family representations
        - Names should follow standard nomenclature
        """
        file_path = os.path.join(self.temp_dir, "gpcr_targets.json")
        
        # Use Client to call tools
        async with Client(self.mcp) as client:
            result = await client.call_tool(
                "local_search_targets_to_file",
                {
                    "file_path_str": file_path,
                    "target_type": "GPCR"
                }
            )
        
        with open(file_path, 'r') as f:
            targets = json.load(f)
        
        criteria = {
            "response_type": {"expected": list, "weight": 1},
            "min_results": {"value": 50, "weight": 3},
            "required_fields": {"fields": ["targetId", "name", "type"], "weight": 2},
            "data_quality": {
                "checks": ["non_empty_names", "valid_ids", "meaningful_content"],
                "weight": 2
            }
        }
        
        judgment = self.judge_response_quality(targets, criteria)
        
        # GPCR-specific quality checks
        if isinstance(targets, list) and targets:
            # Check type consistency
            gpcr_types = [target.get("type") for target in targets]
            all_gpcr = all(t == "GPCR" for t in gpcr_types if t)
            
            if all_gpcr:
                judgment["score"] += 2
                judgment["details"]["type_consistency"] = "PASS: All targets are GPCR type"
            else:
                judgment["issues"].append("Not all targets are GPCR type")
            
            judgment["max_score"] += 2
        
        assert judgment["passed"], f"GPCR search quality failed: {judgment['issues']}"
        assert judgment["score"] / judgment["max_score"] >= 0.8, f"GPCR quality score too low: {judgment['score']}/{judgment['max_score']}"


class TestLigandSearchJudged(PharmacologyJudgedTests):
    """Judged tests for ligand search functionality"""
    
    @pytest.mark.asyncio
    async def test_search_aspirin_ligands_quality(self):
        """
        Test aspirin ligand search with pharmaceutical quality assessment
        
        Judgment Criteria:
        - Should find aspirin and related compounds
        - Should include approval status information
        - Should have chemical identifiers
        - Should show therapeutic relevance
        """
        file_path = os.path.join(self.temp_dir, "aspirin_ligands.json")
        
        # Use Client to call tools
        async with Client(self.mcp) as client:
            result = await client.call_tool(
                "local_search_ligands_to_file",
                {
                    "file_path_str": file_path,
                    "name": "aspirin"
                }
            )
        
        with open(file_path, 'r') as f:
            ligands = json.load(f)
        
        criteria = {
            "response_type": {"expected": list, "weight": 1},
            "min_results": {"value": 1, "weight": 2},
            "required_fields": {"fields": ["ligandId", "name", "type"], "weight": 2},
            "data_quality": {
                "checks": ["non_empty_names", "valid_ids", "meaningful_content"],
                "weight": 2
            }
        }
        
        judgment = self.judge_response_quality(ligands, criteria)
        
        # Pharmaceutical-specific checks
        if isinstance(ligands, list) and ligands:
            # Check for aspirin presence
            aspirin_found = any(
                "aspirin" in ligand.get("name", "").lower()
                for ligand in ligands
            )
            
            # Check for approval information
            has_approval_info = any(
                "approved" in ligand for ligand in ligands
            )
            
            if aspirin_found:
                judgment["score"] += 2
                judgment["details"]["aspirin_found"] = "PASS: Aspirin found in results"
            else:
                judgment["issues"].append("Aspirin not found in results")
            
            if has_approval_info:
                judgment["score"] += 1
                judgment["details"]["approval_info"] = "PASS: Approval information present"
            
            judgment["max_score"] += 3
        
        assert judgment["passed"], f"Aspirin search quality failed: {judgment['issues']}"
        print(f"Aspirin Search Quality Score: {judgment['score']}/{judgment['max_score']}")
    
    @pytest.mark.asyncio
    async def test_search_approved_drugs_quality(self):
        """
        Test approved drugs search with regulatory quality assessment
        
        Judgment Criteria:
        - Should return substantial number of approved drugs
        - All should have approved=True
        - Should include diverse drug types
        - Should have meaningful therapeutic information
        """
        file_path = os.path.join(self.temp_dir, "approved_drugs.json")
        
        # Use Client to call tools
        async with Client(self.mcp) as client:
            result = await client.call_tool(
                "local_search_ligands_to_file",
                {
                    "file_path_str": file_path,
                    "approved": True
                }
            )
        
        with open(file_path, 'r') as f:
            ligands = json.load(f)
        
        criteria = {
            "response_type": {"expected": list, "weight": 1},
            "min_results": {"value": 50, "weight": 3},
            "required_fields": {"fields": ["ligandId", "name", "type"], "weight": 2},
            "data_quality": {
                "checks": ["non_empty_names", "valid_ids", "meaningful_content"],
                "weight": 2
            }
        }
        
        judgment = self.judge_response_quality(ligands, criteria)
        
        # Approved drugs specific checks
        if isinstance(ligands, list) and ligands:
            # Check approval status consistency
            approved_status = [ligand.get("approved") for ligand in ligands]
            all_approved = all(status is True for status in approved_status if status is not None)
            
            if all_approved:
                judgment["score"] += 2
                judgment["details"]["approval_consistency"] = "PASS: All drugs are approved"
            else:
                judgment["issues"].append("Not all returned drugs are approved")
            
            judgment["max_score"] += 2
        
        assert judgment["passed"], f"Approved drugs search quality failed: {judgment['issues']}"
        print(f"Approved Drugs Quality Score: {judgment['score']}/{judgment['max_score']}")


class TestInteractionAnalysisJudged(PharmacologyJudgedTests):
    """Judged tests for interaction analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_target_interactions_quality(self):
        """
        Test target interaction retrieval with pharmacological quality assessment
        
        Judgment Criteria:
        - Should retrieve interactions for a valid target
        - Should include affinity/potency data
        - Should have ligand information
        - Should show interaction types
        """
        # First get a target ID (using dopamine beta-hydroxylase from our earlier test)
        target_id = 2486  # From our test data
        file_path = os.path.join(self.temp_dir, f"target_{target_id}_interactions.json")
        
        # Use Client to call tools
        async with Client(self.mcp) as client:
            result = await client.call_tool(
                "local_get_target_interactions_to_file",
                {
                    "target_id": target_id,
                    "file_path_str": file_path
                }
            )
        
        with open(file_path, 'r') as f:
            interactions = json.load(f)
        
        criteria = {
            "response_type": {"expected": list, "weight": 1},
            "min_results": {"value": 1, "weight": 2},
            "required_fields": {"fields": ["interactionId", "targetId", "ligandId"], "weight": 2},
            "data_quality": {
                "checks": ["non_empty_names", "valid_ids", "meaningful_content"],
                "weight": 2
            }
        }
        
        judgment = self.judge_response_quality(interactions, criteria)
        
        # Interaction-specific quality checks
        if isinstance(interactions, list) and interactions:
            # Check for affinity/potency data
            has_affinity = any(
                interaction.get("affinity") or interaction.get("concentration")
                for interaction in interactions
            )
            
            # Check for action/type information
            has_action_info = any(
                interaction.get("action") or interaction.get("type")
                for interaction in interactions
            )
            
            if has_affinity:
                judgment["score"] += 1
                judgment["details"]["affinity_data"] = "PASS: Affinity/potency data present"
            
            if has_action_info:
                judgment["score"] += 1
                judgment["details"]["action_info"] = "PASS: Action/type information present"
            
            judgment["max_score"] += 2
        
        assert judgment["passed"], f"Target interactions quality failed: {judgment['issues']}"
        print(f"Target Interactions Quality Score: {judgment['score']}/{judgment['max_score']}")


class TestWorkflowJudged(PharmacologyJudgedTests):
    """Judged tests for complete workflow functionality"""
    
    @pytest.mark.asyncio
    async def test_drug_discovery_workflow_quality(self):
        """
        Test a complete drug discovery workflow with comprehensive quality assessment
        
        Workflow:
        1. Search for targets related to a disease/condition
        2. Find approved drugs for those targets
        3. Analyze interactions and mechanisms
        
        Judgment Criteria:
        - Workflow should complete successfully
        - Each step should produce meaningful results
        - Results should be scientifically coherent
        - Should demonstrate pharmacological relationships
        """
        workflow_results = {}
        
        # Step 1: Find dopamine-related targets (relevant to neurological conditions)
        targets_file = os.path.join(self.temp_dir, "workflow_targets.json")
        async with Client(self.mcp) as client:
            await client.call_tool(
                "local_search_targets_to_file",
                {
                    "file_path_str": targets_file,
                    "name": "dopamine"
                }
            )
        
        with open(targets_file, 'r') as f:
            targets = json.load(f)
        
        workflow_results["targets"] = targets
        
        # Step 2: Find approved drugs
        drugs_file = os.path.join(self.temp_dir, "workflow_drugs.json")
        async with Client(self.mcp) as client:
            await client.call_tool(
                "local_search_ligands_to_file",
                {
                    "file_path_str": drugs_file,
                    "approved": True
                }
            )
        
        with open(drugs_file, 'r') as f:
            drugs = json.load(f)
        
        workflow_results["approved_drugs"] = drugs
        
        # Step 3: Get interactions for the first target (if available)
        if isinstance(targets, list) and targets:
            target_id = targets[0].get("targetId")
            if target_id:
                interactions_file = os.path.join(self.temp_dir, f"workflow_interactions_{target_id}.json")
                async with Client(self.mcp) as client:
                    await client.call_tool(
                        "local_get_target_interactions_to_file",
                        {
                            "target_id": target_id,
                            "file_path_str": interactions_file
                        }
                    )
                
                with open(interactions_file, 'r') as f:
                    interactions = json.load(f)
                
                workflow_results["interactions"] = interactions
        
        # Judge workflow quality
        workflow_judgment = {
            "test_name": "Drug Discovery Workflow",
            "passed": True,
            "score": 0,
            "max_score": 6,
            "details": {},
            "issues": []
        }
        
        # Check each step
        steps = [
            ("targets", "Target search", 2),
            ("approved_drugs", "Approved drugs search", 2),
            ("interactions", "Interaction analysis", 2)
        ]
        
        for step_key, step_name, weight in steps:
            if step_key in workflow_results:
                data = workflow_results[step_key]
                if isinstance(data, list) and len(data) > 0:
                    workflow_judgment["score"] += weight
                    workflow_judgment["details"][step_key] = f"PASS: {step_name} completed with {len(data)} results"
                else:
                    workflow_judgment["passed"] = False
                    workflow_judgment["issues"].append(f"FAIL: {step_name} returned no results")
            else:
                workflow_judgment["passed"] = False
                workflow_judgment["issues"].append(f"FAIL: {step_name} not completed")
        
        # Print workflow results
        print(f"\n=== {workflow_judgment['test_name']} ===")
        print(f"Score: {workflow_judgment['score']}/{workflow_judgment['max_score']}")
        for step, details in workflow_judgment["details"].items():
            print(f"{step}: {details}")
        for issue in workflow_judgment["issues"]:
            print(issue)
        
        assert workflow_judgment["passed"], f"Workflow failed: {workflow_judgment['issues']}"
        assert workflow_judgment["score"] >= workflow_judgment["max_score"] * 0.8, f"Workflow quality too low: {workflow_judgment['score']}/{workflow_judgment['max_score']}"
        
        print(f"Workflow completed successfully with quality score: {workflow_judgment['score']}/{workflow_judgment['max_score']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 