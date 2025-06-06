import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import json

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, mocked)"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that test API endpoints"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )

# Shared fixtures for all tests
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup after test
    shutil.rmtree(temp_path)

@pytest.fixture
def temp_file(temp_dir):
    """Create a temporary file for testing"""
    file_path = Path(temp_dir) / "test_file.json"
    yield file_path
    # File will be cleaned up with temp_dir

# Mock data fixtures that can be reused across test files
@pytest.fixture
def sample_target_data():
    """Sample target data for testing - consistent across all tests"""
    return {
        "targetId": 1,
        "name": "5-HT<sub>1A</sub> receptor",
        "abbreviation": "5-HT1A",
        "systematicName": "5-hydroxytryptamine receptor 1A",
        "type": "GPCR",
        "familyIds": [1],
        "subunitIds": [],
        "complexIds": []
    }

@pytest.fixture
def sample_ligand_data():
    """Sample ligand data for testing - consistent across all tests"""
    return {
        "ligandId": 1,
        "name": "5-HT",
        "abbreviation": "5-HT",
        "inn": "serotonin",
        "type": "Endogenous peptide",
        "species": "Human",
        "radioactive": False,
        "labelled": False,
        "approved": False,
        "withdrawn": False,
        "approvalSource": None
    }

@pytest.fixture
def sample_interaction_data():
    """Sample interaction data for testing - consistent across all tests"""
    return {
        "interactionId": 1,
        "targetId": 1,
        "ligandId": 1,
        "targetSpecies": "Human",
        "primaryTarget": True,
        "type": "Agonist",
        "action": "Agonist",
        "affinity": "8.4",
        "affinityType": "pKi",
        "endogenous": True
    }

@pytest.fixture
def sample_disease_data():
    """Sample disease data for testing - consistent across all tests"""
    return {
        "diseaseId": 1,
        "name": "Depression",
        "description": "Major depressive disorder",
        "synonyms": ["MDD", "Clinical depression"]
    }

@pytest.fixture
def sample_family_data():
    """Sample target family data for testing"""
    return {
        "familyId": 1,
        "name": "5-Hydroxytryptamine receptors",
        "targetIds": [1, 2, 5],
        "parentFamilyIds": [694],
        "subFamilyIds": [9]
    }

# Mock response fixtures for HTTP testing
@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response object"""
    def _create_response(status_code=200, json_data=None, text=""):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = text
        if json_data is not None:
            mock_response.json.return_value = json_data
        else:
            mock_response.json.side_effect = json.JSONDecodeError("No JSON", "", 0)
        return mock_response
    return _create_response

@pytest.fixture
def mock_successful_response(mock_http_response, sample_target_data):
    """Create a mock successful HTTP response with target data"""
    return mock_http_response(200, [sample_target_data])

@pytest.fixture
def mock_empty_response(mock_http_response):
    """Create a mock successful HTTP response with empty data"""
    return mock_http_response(200, [])

@pytest.fixture
def mock_error_response(mock_http_response):
    """Create a mock error HTTP response"""
    return mock_http_response(500, text="Internal Server Error")

@pytest.fixture
def mock_not_found_response(mock_http_response):
    """Create a mock 404 HTTP response"""
    return mock_http_response(404, text="Not Found")

# Test data collections for parametrized tests
@pytest.fixture
def target_types():
    """List of valid target types for parametrized testing"""
    return ["GPCR", "Enzyme", "Ion channel", "Nuclear hormone receptor", "Transporter"]

@pytest.fixture
def ligand_types():
    """List of valid ligand types for parametrized testing"""
    return ["Synthetic organic", "Natural product", "Endogenous peptide", "Antibody"]

@pytest.fixture
def species_list():
    """List of valid species for parametrized testing"""
    return ["Human", "Mouse", "Rat", "Dog", "Rabbit"]

@pytest.fixture
def affinity_types():
    """List of valid affinity types for parametrized testing"""
    return ["pKi", "pIC50", "pEC50", "pKd", "pA2"]

# Complex test data for edge cases
@pytest.fixture
def large_target_dataset(sample_target_data):
    """Create a large dataset for performance testing"""
    targets = []
    for i in range(1000):
        target = sample_target_data.copy()
        target["targetId"] = i + 1
        target["name"] = f"Target {i + 1}"
        targets.append(target)
    return targets

@pytest.fixture
def malformed_target_data():
    """Create malformed target data for error handling tests"""
    return [
        {"name": "Target without ID"},
        {"targetId": "not_a_number", "name": "Invalid ID"},
        {"targetId": 1},  # Missing name
        {}  # Empty object
    ]

# API endpoint collections for testing
@pytest.fixture
def target_endpoints():
    """List of target-related endpoints for testing"""
    return [
        "/targets/1",
        "/targets/1/interactions",
        "/targets/1/synonyms",
        "/targets/1/geneProteinInformation",
        "/targets/1/databaseLinks",
        "/targets/1/naturalLigands",
        "/targets/1/function",
        "/targets/1/diseases"
    ]

@pytest.fixture
def ligand_endpoints():
    """List of ligand-related endpoints for testing"""
    return [
        "/ligands/1",
        "/ligands/1/interactions",
        "/ligands/1/synonyms",
        "/ligands/1/databaseLinks"
    ]

# Test utilities
@pytest.fixture
def assert_valid_response():
    """Utility function to assert valid API responses"""
    def _assert_valid_response(response, expected_status=200, expected_type=list):
        assert response.status_code == expected_status
        if expected_status == 200:
            data = response.json()
            assert isinstance(data, expected_type)
            return data
        return None
    return _assert_valid_response

@pytest.fixture
def assert_valid_target():
    """Utility function to assert valid target data structure"""
    def _assert_valid_target(target_data):
        required_fields = ["targetId", "name", "type"]
        for field in required_fields:
            assert field in target_data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(target_data["targetId"], int)
        assert isinstance(target_data["name"], str)
        assert isinstance(target_data["type"], str)
        
        # Validate optional fields if present
        if "familyIds" in target_data:
            assert isinstance(target_data["familyIds"], list)
        if "subunitIds" in target_data:
            assert isinstance(target_data["subunitIds"], list)
        if "complexIds" in target_data:
            assert isinstance(target_data["complexIds"], list)
    
    return _assert_valid_target

@pytest.fixture
def assert_valid_ligand():
    """Utility function to assert valid ligand data structure"""
    def _assert_valid_ligand(ligand_data):
        required_fields = ["ligandId", "name"]
        for field in required_fields:
            assert field in ligand_data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(ligand_data["ligandId"], int)
        assert isinstance(ligand_data["name"], str)
        
        # Validate boolean fields if present
        boolean_fields = ["radioactive", "labelled", "approved", "withdrawn"]
        for field in boolean_fields:
            if field in ligand_data:
                assert isinstance(ligand_data[field], bool)
    
    return _assert_valid_ligand

@pytest.fixture
def assert_valid_interaction():
    """Utility function to assert valid interaction data structure"""
    def _assert_valid_interaction(interaction_data):
        required_fields = ["interactionId", "targetId", "ligandId"]
        for field in required_fields:
            assert field in interaction_data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(interaction_data["interactionId"], int)
        assert isinstance(interaction_data["targetId"], int)
        assert isinstance(interaction_data["ligandId"], int)
        
        # Validate optional boolean fields
        boolean_fields = ["primaryTarget", "endogenous"]
        for field in boolean_fields:
            if field in interaction_data:
                assert isinstance(interaction_data[field], bool)
    
    return _assert_valid_interaction

# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Utility for timing test operations"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()

# Test markers for organizing test runs
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names and locations"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid or "test_pharmacology_api.py" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests (mocked tests)
        if "mocked" in item.nodeid or "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Mark API tests
        if "api" in item.nodeid or any(endpoint in item.nodeid for endpoint in ["target", "ligand", "interaction", "disease"]):
            item.add_marker(pytest.mark.api)
        
        # Mark slow tests
        if "large" in item.name or "performance" in item.name or "concurrent" in item.name:
            item.add_marker(pytest.mark.slow) 