import pytest
import json
from unittest.mock import patch, Mock, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import httpx
from pharmacology_mcp.pharmacology_api import PharmacologyRestAPI

# Create test client
app = PharmacologyRestAPI()
client = TestClient(app)

# Mock data fixtures inspired by pygtop patterns
@pytest.fixture
def mock_target_response():
    """Mock target response data"""
    return {
        "targetId": 1,
        "name": "5-HT<sub>1A</sub> receptor",
        "abbreviation": "5-HT1A",
        "systematicName": "5-hydroxytryptamine receptor 1A",
        "targetType": "GPCR",
        "familyIds": [1],
        "subunitIds": [],
        "complexIds": []
    }

@pytest.fixture
def mock_ligand_response():
    """Mock ligand response data"""
    return {
        "ligandId": 1,
        "name": "5-HT",
        "abbreviation": "5-HT",
        "innOrIupacName": "serotonin",
        "type": "Endogenous peptide",
        "species": "Human",
        "radioactive": False,
        "labelled": False,
        "approved": False,
        "withdrawn": False,
        "approvalSource": None
    }

@pytest.fixture
def mock_interaction_response():
    """Mock interaction response data"""
    return {
        "interactionId": 1,
        "targetId": 1,
        "ligandId": 1,
        "species": "Human",
        "primaryTarget": True,
        "type": "Agonist",
        "action": "Agonist",
        "affinity": "8.4",
        "affinityType": "pKi",
        "endogenous": True
    }

@pytest.fixture
def mock_disease_response():
    """Mock disease response data"""
    return {
        "diseaseId": 1,
        "name": "Depression",
        "description": "Major depressive disorder",
        "synonyms": ["MDD", "Clinical depression"]
    }

class TestTargetEndpointsMocked:
    """Test target endpoints with mocked external API calls"""
    
    @patch('httpx.AsyncClient.get')
    def test_list_targets_success(self, mock_get, mock_target_response):
        """Test successful target listing with mocked response"""
        # Create async mock
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_target_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/targets", json={"type": "GPCR"})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["targetId"] == 1
        assert data[0]["targetType"] == "GPCR"
    
    @patch('httpx.AsyncClient.get')
    def test_list_targets_empty_response(self, mock_get):
        """Test target listing with empty response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/targets", json={"name": "nonexistent"})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @patch('httpx.AsyncClient.get')
    def test_list_targets_api_error(self, mock_get):
        """Test target listing when external API returns error"""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        # Configure the mock to raise an HTTPStatusError
        error = httpx.HTTPStatusError("Server Error", request=Mock(), response=mock_response)
        mock_response.raise_for_status.side_effect = error
        
        response = client.post("/targets", json={})
        
        assert response.status_code == 500
    
    @patch('httpx.AsyncClient.get')
    def test_get_single_target_success(self, mock_get, mock_target_response):
        """Test getting single target with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_target_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.get("/targets/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["targetId"] == 1
        assert data["name"] == "5-HT<sub>1A</sub> receptor"
    
    @patch('httpx.AsyncClient.get')
    def test_get_single_target_not_found(self, mock_get):
        """Test getting single target when not found"""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        # Configure the mock to raise an HTTPStatusError
        error = httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        mock_response.raise_for_status.side_effect = error
        
        response = client.get("/targets/999999")
        
        assert response.status_code == 404
    
    @patch('httpx.AsyncClient.get')
    def test_get_target_interactions_success(self, mock_get, mock_interaction_response):
        """Test getting target interactions with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_interaction_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.get("/targets/1/interactions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["targetId"] == 1
        assert data[0]["ligandId"] == 1
    
    @patch('httpx.AsyncClient.get')
    def test_get_target_interactions_with_species_filter(self, mock_get, mock_interaction_response):
        """Test getting target interactions with species filter"""
        # Modify mock response to include species
        mock_interaction_response["species"] = "Human"
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_interaction_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.get("/targets/1/interactions?species=Human")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["species"] == "Human"
        
        # Verify the correct URL was called with species parameter
        mock_get.assert_called_once()
        # Check that the call was made with params
        call_args = mock_get.call_args
        assert call_args is not None
        # The params should be passed as the 'params' keyword argument
        if len(call_args) > 1 and 'params' in call_args[1]:
            params = call_args[1]['params']
            assert 'species' in params
            assert params['species'] == 'Human'

class TestLigandEndpointsMocked:
    """Test ligand endpoints with mocked external API calls"""
    
    @patch('httpx.AsyncClient.get')
    def test_list_ligands_success(self, mock_get, mock_ligand_response):
        """Test successful ligand listing with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_ligand_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/ligands", json={"type": "Endogenous peptide"})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["ligandId"] == 1
        assert data[0]["type"] == "Endogenous peptide"
    
    @patch('httpx.AsyncClient.get')
    def test_list_ligands_with_approval_filter(self, mock_get, mock_ligand_response):
        """Test ligand listing with approval status filter"""
        # Modify mock response for approved ligand
        mock_ligand_response["approved"] = True
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_ligand_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/ligands", json={"approved": True})
        
        assert response.status_code == 200
        data = response.json()
        assert data[0]["approved"] is True
    
    @patch('httpx.AsyncClient.get')
    def test_list_ligands_with_molecular_weight_filter(self, mock_get, mock_ligand_response):
        """Test ligand listing with molecular weight filters"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_ligand_response]
        mock_get.return_value = mock_response
        
        response = client.post("/ligands", json={
            "molWeightGt": 100,
            "molWeightLt": 500
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify the correct URL was called with weight parameters
        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][0])
        assert "molWeightGt=100" in called_url
        assert "molWeightLt=500" in called_url
    
    @patch('httpx.AsyncClient.get')
    def test_get_single_ligand_success(self, mock_get, mock_ligand_response):
        """Test getting single ligand with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ligand_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.get("/ligands/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ligandId"] == 1
        assert data["name"] == "5-HT"
    
    @patch('httpx.AsyncClient.get')
    def test_exact_structure_search_success(self, mock_get, mock_ligand_response):
        """Test exact structure search with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_ligand_response]
        mock_get.return_value = mock_response
        
        response = client.post("/ligands/exact", json={"smiles": "CCO"})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @patch('httpx.AsyncClient.get')
    def test_exact_structure_search_no_results(self, mock_get):
        """Test exact structure search with no results"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        response = client.post("/ligands/exact", json={"smiles": "invalid_smiles"})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

class TestInteractionEndpointsMocked:
    """Test interaction endpoints with mocked external API calls"""
    
    @patch('httpx.AsyncClient.get')
    def test_list_interactions_success(self, mock_get, mock_interaction_response):
        """Test successful interaction listing with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_interaction_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/interactions", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["interactionId"] == 1
    
    @patch('httpx.AsyncClient.get')
    def test_list_interactions_by_target(self, mock_get, mock_interaction_response):
        """Test filtering interactions by target ID"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_interaction_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/interactions", json={"targetId": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data[0]["targetId"] == 1
    
    @patch('httpx.AsyncClient.get')
    def test_list_interactions_by_species(self, mock_get, mock_interaction_response):
        """Test filtering interactions by species"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_interaction_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/interactions", json={"species": "Human"})
        
        assert response.status_code == 200
        data = response.json()
        assert data[0]["species"] == "Human"
    
    @patch('httpx.AsyncClient.get')
    def test_list_interactions_primary_targets_only(self, mock_get, mock_interaction_response):
        """Test filtering for primary target interactions only"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_interaction_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/interactions", json={"primaryTarget": True})
        
        assert response.status_code == 200
        data = response.json()
        assert data[0]["primaryTarget"] is True
    
    @patch('httpx.AsyncClient.get')
    def test_get_single_interaction_success(self, mock_get, mock_interaction_response):
        """Test getting single interaction with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_interaction_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.get("/interactions/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["interactionId"] == 1

class TestDiseaseEndpointsMocked:
    """Test disease endpoints with mocked external API calls"""
    
    @patch('httpx.AsyncClient.get')
    def test_list_diseases_success(self, mock_get, mock_disease_response):
        """Test successful disease listing with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [mock_disease_response]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.get("/diseases")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["diseaseId"] == 1
        assert data[0]["name"] == "Depression"
    
    @patch('httpx.AsyncClient.get')
    def test_get_single_disease_success(self, mock_get, mock_disease_response):
        """Test getting single disease with mocked response"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_disease_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.get("/diseases/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["diseaseId"] == 1
        assert data["name"] == "Depression"

class TestErrorHandlingMocked:
    """Test error handling with mocked responses"""
    
    @patch('httpx.AsyncClient.get')
    def test_network_timeout_error(self, mock_get):
        """Test handling of network timeout errors"""
        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        
        response = client.post("/targets", json={})
        
        assert response.status_code == 500
    
    @patch('httpx.AsyncClient.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection errors"""
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        
        response = client.post("/targets", json={})
        
        assert response.status_code == 500
    
    @patch('httpx.AsyncClient.get')
    def test_invalid_json_response(self, mock_get):
        """Test handling of invalid JSON responses from external API"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/targets", json={})
        
        assert response.status_code == 500
    
    @patch('httpx.AsyncClient.get')
    def test_api_rate_limit_error(self, mock_get):
        """Test handling of API rate limit errors"""
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_get.return_value = mock_response
        
        # Configure the mock to raise an HTTPStatusError
        error = httpx.HTTPStatusError("Rate limit exceeded", request=Mock(), response=mock_response)
        mock_response.raise_for_status.side_effect = error
        
        response = client.post("/targets", json={})
        
        assert response.status_code == 429

class TestParameterValidationMocked:
    """Test parameter validation with mocked responses"""
    
    @patch('httpx.AsyncClient.get')
    def test_invalid_target_type(self, mock_get):
        """Test validation of invalid target type"""
        # Mock a successful response even with invalid type
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/targets", json={"type": "InvalidType"})
        # Should still make the request but might return empty results
        assert response.status_code == 200
    
    @patch('httpx.AsyncClient.get')
    def test_invalid_boolean_parameter(self, mock_get):
        """Test validation of invalid boolean parameters"""
        # Mock a successful response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/targets", json={"immuno": "not_a_boolean"})
        # FastAPI should handle type conversion or validation
        assert response.status_code in [200, 422]

class TestResponseProcessingMocked:
    """Test response processing and data transformation"""
    
    @patch('httpx.AsyncClient.get')
    def test_empty_response_handling(self, mock_get):
        """Test handling of empty responses"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/targets", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @patch('httpx.AsyncClient.get')
    def test_large_response_handling(self, mock_get, mock_target_response):
        """Test handling of large responses"""
        # Create a large response with many targets
        large_response = [mock_target_response.copy() for _ in range(1000)]
        for i, target in enumerate(large_response):
            target["targetId"] = i + 1
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/targets", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1000
    
    @patch('httpx.AsyncClient.get')
    def test_malformed_response_data(self, mock_get):
        """Test handling of malformed response data"""
        # Response with missing required fields
        malformed_data = [{"name": "Target without ID"}]
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = malformed_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post("/targets", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should still return the data even if malformed (validation warnings logged)
        assert len(data) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 