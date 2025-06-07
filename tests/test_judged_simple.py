"""
Simple Judged Tests for Pharmacology MCP Server
Inspired by opengenes-mcp testing patterns

These tests validate both functionality and response quality using real API calls.
Simplified version focusing on core functionality.
"""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path

# Import the local MCP tools directly
from src.pharmacology_mcp.local import (
    search_targets_to_file,
    search_ligands_to_file,
    get_target_interactions_to_file,
    get_ligand_interactions_to_file
)


class TestPharmacologyMCPJudged:
    """Simple judged tests for pharmacology MCP functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def judge_results(self, data, test_name, criteria):
        """Simple judgment function for test results"""
        judgment = {
            "test_name": test_name,
            "passed": True,
            "score": 0,
            "max_score": len(criteria),
            "details": [],
            "issues": []
        }
        
        for criterion in criteria:
            if criterion == "is_list":
                if isinstance(data, list):
                    judgment["score"] += 1
                    judgment["details"].append("✓ Response is a list")
                else:
                    judgment["passed"] = False
                    judgment["issues"].append("✗ Response is not a list")
            
            elif criterion == "has_results":
                if isinstance(data, list) and len(data) > 0:
                    judgment["score"] += 1
                    judgment["details"].append(f"✓ Found {len(data)} results")
                else:
                    judgment["passed"] = False
                    judgment["issues"].append("✗ No results found")
            
            elif criterion == "has_required_fields":
                if isinstance(data, list) and data:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        # Check for common required fields
                        required = ["name"] + ([k for k in first_item.keys() if k.endswith("Id")])
                        if all(field in first_item for field in required[:2]):  # Check at least name and one ID
                            judgment["score"] += 1
                            judgment["details"].append("✓ Required fields present")
                        else:
                            judgment["issues"].append("✗ Missing required fields")
                    else:
                        judgment["issues"].append("✗ Results are not dictionaries")
                else:
                    judgment["issues"].append("✗ No data to check fields")
            
            elif criterion == "meaningful_content":
                if isinstance(data, list) and data:
                    meaningful = any(
                        isinstance(item, dict) and 
                        item.get("name") and 
                        len(str(item.get("name", ""))) > 2
                        for item in data
                    )
                    if meaningful:
                        judgment["score"] += 1
                        judgment["details"].append("✓ Contains meaningful content")
                    else:
                        judgment["issues"].append("✗ Content appears empty or meaningless")
                else:
                    judgment["issues"].append("✗ No data to check content")
        
        return judgment
    
    @pytest.mark.asyncio
    async def test_search_dopamine_targets_judged(self):
        """
        Judged test: Search for dopamine-related targets
        
        Success criteria:
        1. Returns a list
        2. Contains at least some results
        3. Results have required fields (name, targetId)
        4. Content is meaningful (non-empty names)
        """
        file_path = os.path.join(self.temp_dir, "dopamine_targets.json")
        
        # Execute the search
        result_path = await search_targets_to_file(
            file_path_str=file_path,
            name="dopamine"
        )
        
        # Verify file was created
        assert os.path.exists(file_path), "Results file should be created"
        assert result_path == file_path, "Returned path should match input path"
        
        # Load and judge results
        with open(file_path, 'r') as f:
            targets = json.load(f)
        
        judgment = self.judge_results(
            targets, 
            "Dopamine Targets Search",
            ["is_list", "has_results", "has_required_fields", "meaningful_content"]
        )
        
        # Additional dopamine-specific check
        if isinstance(targets, list) and targets:
            dopamine_relevant = any(
                "dopamine" in str(target.get("name", "")).lower()
                for target in targets
            )
            if dopamine_relevant:
                judgment["score"] += 1
                judgment["details"].append("✓ Found dopamine-relevant targets")
            else:
                judgment["issues"].append("✗ No clearly dopamine-relevant targets")
            judgment["max_score"] += 1
        
        # Print judgment
        print(f"\n=== {judgment['test_name']} ===")
        print(f"Score: {judgment['score']}/{judgment['max_score']}")
        for detail in judgment["details"]:
            print(detail)
        for issue in judgment["issues"]:
            print(issue)
        
        # Assert quality standards
        assert judgment["passed"], f"Test failed: {judgment['issues']}"
        assert judgment["score"] >= judgment["max_score"] * 0.8, f"Quality too low: {judgment['score']}/{judgment['max_score']}"
    
    @pytest.mark.asyncio
    async def test_search_aspirin_ligands_judged(self):
        """
        Judged test: Search for aspirin-related ligands
        
        Success criteria:
        1. Returns a list
        2. Contains results
        3. Results have required fields
        4. Content is meaningful
        5. Aspirin is found in results
        """
        file_path = os.path.join(self.temp_dir, "aspirin_ligands.json")
        
        result_path = await search_ligands_to_file(
            file_path_str=file_path,
            name="aspirin"
        )
        
        assert os.path.exists(file_path), "Results file should be created"
        
        with open(file_path, 'r') as f:
            ligands = json.load(f)
        
        judgment = self.judge_results(
            ligands,
            "Aspirin Ligands Search", 
            ["is_list", "has_results", "has_required_fields", "meaningful_content"]
        )
        
        # Aspirin-specific check
        if isinstance(ligands, list) and ligands:
            aspirin_found = any(
                "aspirin" in str(ligand.get("name", "")).lower()
                for ligand in ligands
            )
            if aspirin_found:
                judgment["score"] += 1
                judgment["details"].append("✓ Aspirin found in results")
            else:
                judgment["issues"].append("✗ Aspirin not found in results")
            judgment["max_score"] += 1
        
        print(f"\n=== {judgment['test_name']} ===")
        print(f"Score: {judgment['score']}/{judgment['max_score']}")
        for detail in judgment["details"]:
            print(detail)
        for issue in judgment["issues"]:
            print(issue)
        
        assert judgment["passed"], f"Test failed: {judgment['issues']}"
        assert judgment["score"] >= judgment["max_score"] * 0.8, f"Quality too low: {judgment['score']}/{judgment['max_score']}"
    
    @pytest.mark.asyncio
    async def test_gpcr_targets_comprehensive_judged(self):
        """
        Judged test: Search for GPCR targets (comprehensive)
        
        Success criteria:
        1. Returns a list
        2. Contains substantial results (>20)
        3. All results are GPCR type
        4. Content is meaningful
        """
        file_path = os.path.join(self.temp_dir, "gpcr_targets.json")
        
        result_path = await search_targets_to_file(
            file_path_str=file_path,
            target_type="GPCR"
        )
        
        assert os.path.exists(file_path), "Results file should be created"
        
        with open(file_path, 'r') as f:
            targets = json.load(f)
        
        judgment = self.judge_results(
            targets,
            "GPCR Targets Search",
            ["is_list", "has_results", "has_required_fields", "meaningful_content"]
        )
        
        # GPCR-specific checks
        if isinstance(targets, list):
            # Check for substantial results
            if len(targets) >= 20:
                judgment["score"] += 1
                judgment["details"].append(f"✓ Substantial results: {len(targets)} targets")
            else:
                judgment["issues"].append(f"✗ Insufficient results: {len(targets)} < 20")
            
            # Check type consistency
            if targets:
                gpcr_types = [target.get("type") for target in targets]
                all_gpcr = all(t == "GPCR" for t in gpcr_types if t)
                if all_gpcr:
                    judgment["score"] += 1
                    judgment["details"].append("✓ All targets are GPCR type")
                else:
                    judgment["issues"].append("✗ Not all targets are GPCR type")
            
            judgment["max_score"] += 2
        
        print(f"\n=== {judgment['test_name']} ===")
        print(f"Score: {judgment['score']}/{judgment['max_score']}")
        for detail in judgment["details"]:
            print(detail)
        for issue in judgment["issues"]:
            print(issue)
        
        assert judgment["passed"], f"Test failed: {judgment['issues']}"
        assert judgment["score"] >= judgment["max_score"] * 0.7, f"Quality too low: {judgment['score']}/{judgment['max_score']}"
    
    @pytest.mark.asyncio
    async def test_target_interactions_judged(self):
        """
        Judged test: Get interactions for a specific target
        
        Success criteria:
        1. Returns a list
        2. Contains interaction data
        3. Has required fields
        4. Shows pharmacological relevance
        """
        # Use dopamine beta-hydroxylase target ID from our test data
        target_id = 2486
        file_path = os.path.join(self.temp_dir, f"target_{target_id}_interactions.json")
        
        result_path = await get_target_interactions_to_file(
            target_id=target_id,
            file_path_str=file_path
        )
        
        assert os.path.exists(file_path), "Results file should be created"
        
        with open(file_path, 'r') as f:
            interactions = json.load(f)
        
        judgment = self.judge_results(
            interactions,
            f"Target {target_id} Interactions",
            ["is_list", "has_results", "has_required_fields", "meaningful_content"]
        )
        
        # Interaction-specific checks
        if isinstance(interactions, list) and interactions:
            # Check for pharmacological data
            has_affinity = any(
                interaction.get("affinity") or interaction.get("affinityParameter")
                for interaction in interactions
            )
            has_action = any(
                interaction.get("action") or interaction.get("type")
                for interaction in interactions
            )
            
            if has_affinity:
                judgment["score"] += 1
                judgment["details"].append("✓ Contains affinity data")
            else:
                judgment["issues"].append("✗ No affinity data found")
            
            if has_action:
                judgment["score"] += 1
                judgment["details"].append("✓ Contains action/type data")
            else:
                judgment["issues"].append("✗ No action/type data found")
            
            judgment["max_score"] += 2
        
        print(f"\n=== {judgment['test_name']} ===")
        print(f"Score: {judgment['score']}/{judgment['max_score']}")
        for detail in judgment["details"]:
            print(detail)
        for issue in judgment["issues"]:
            print(issue)
        
        assert judgment["passed"], f"Test failed: {judgment['issues']}"
        assert judgment["score"] >= judgment["max_score"] * 0.6, f"Quality too low: {judgment['score']}/{judgment['max_score']}"
    
    @pytest.mark.asyncio
    async def test_workflow_integration_judged(self):
        """
        Judged test: Complete workflow integration
        
        Workflow:
        1. Search for targets
        2. Search for ligands
        3. Get interactions
        
        Success criteria:
        1. All steps complete successfully
        2. Results are coherent
        3. Data quality is maintained
        """
        workflow_judgment = {
            "test_name": "Complete Workflow Integration",
            "passed": True,
            "score": 0,
            "max_score": 6,
            "details": [],
            "issues": []
        }
        
        # Step 1: Search targets
        targets_file = os.path.join(self.temp_dir, "workflow_targets.json")
        await search_targets_to_file(
            file_path_str=targets_file,
            name="dopamine"
        )
        
        if os.path.exists(targets_file):
            with open(targets_file, 'r') as f:
                targets = json.load(f)
            if isinstance(targets, list) and targets:
                workflow_judgment["score"] += 2
                workflow_judgment["details"].append(f"✓ Step 1: Found {len(targets)} targets")
            else:
                workflow_judgment["issues"].append("✗ Step 1: No targets found")
        else:
            workflow_judgment["passed"] = False
            workflow_judgment["issues"].append("✗ Step 1: Targets file not created")
        
        # Step 2: Search ligands
        ligands_file = os.path.join(self.temp_dir, "workflow_ligands.json")
        await search_ligands_to_file(
            file_path_str=ligands_file,
            approved=True
        )
        
        if os.path.exists(ligands_file):
            with open(ligands_file, 'r') as f:
                ligands = json.load(f)
            if isinstance(ligands, list) and ligands:
                workflow_judgment["score"] += 2
                workflow_judgment["details"].append(f"✓ Step 2: Found {len(ligands)} ligands")
            else:
                workflow_judgment["issues"].append("✗ Step 2: No ligands found")
        else:
            workflow_judgment["passed"] = False
            workflow_judgment["issues"].append("✗ Step 2: Ligands file not created")
        
        # Step 3: Get interactions (if we have targets)
        if 'targets' in locals() and targets:
            target_id = targets[0].get("targetId")
            if target_id:
                interactions_file = os.path.join(self.temp_dir, "workflow_interactions.json")
                await get_target_interactions_to_file(
                    target_id=target_id,
                    file_path_str=interactions_file
                )
                
                if os.path.exists(interactions_file):
                    with open(interactions_file, 'r') as f:
                        interactions = json.load(f)
                    if isinstance(interactions, list):
                        workflow_judgment["score"] += 2
                        workflow_judgment["details"].append(f"✓ Step 3: Found {len(interactions)} interactions")
                    else:
                        workflow_judgment["issues"].append("✗ Step 3: Invalid interactions data")
                else:
                    workflow_judgment["issues"].append("✗ Step 3: Interactions file not created")
            else:
                workflow_judgment["issues"].append("✗ Step 3: No target ID available")
        else:
            workflow_judgment["issues"].append("✗ Step 3: No targets available for interaction search")
        
        print(f"\n=== {workflow_judgment['test_name']} ===")
        print(f"Score: {workflow_judgment['score']}/{workflow_judgment['max_score']}")
        for detail in workflow_judgment["details"]:
            print(detail)
        for issue in workflow_judgment["issues"]:
            print(issue)
        
        assert workflow_judgment["passed"], f"Workflow failed: {workflow_judgment['issues']}"
        assert workflow_judgment["score"] >= 4, f"Workflow quality too low: {workflow_judgment['score']}/{workflow_judgment['max_score']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 