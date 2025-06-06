import pytest
import httpx
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from src.pharmacology_mcp.pharmacology_api import PharmacologyRestAPI

# Create test client
app = PharmacologyRestAPI()
client = TestClient(app)

# Test data fixtures inspired by pygtop patterns
@pytest.fixture
def sample_target_data():
    """Sample target data for testing"""
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
    """Sample ligand data for testing"""
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
    """Sample interaction data for testing"""
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
    """Sample disease data for testing"""
    return {
        "diseaseId": 1,
        "name": "Depression",
        "description": "Major depressive disorder",
        "synonyms": ["MDD", "Clinical depression"]
    }

class TestTargetEndpoints:
    """Test target-related endpoints"""
    
    def test_list_targets_no_filters(self):
        """Test listing targets with no filters"""
        response = client.post("/targets", json={})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_targets_with_type_filter(self):
        """Test filtering targets by type"""
        response = client.post("/targets", json={"type": "GPCR"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that returned targets are GPCRs (if any returned)
        for target in data[:3]:  # Check first 3
            if "targetType" in target:
                assert target["targetType"] == "GPCR"
    
    def test_list_targets_with_name_filter(self):
        """Test filtering targets by name"""
        response = client.post("/targets", json={"name": "adrenergic"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that returned targets contain the search term
        for target in data[:3]:  # Check first 3
            if "name" in target:
                # The API returns HTML entities, so we need to handle that
                name_lower = target["name"].lower()
                assert "adren" in name_lower or "adr" in name_lower
    
    def test_get_single_target(self):
        """Test getting a single target by ID"""
        # Use a known target ID (5-HT1A receptor)
        response = client.get("/targets/1")
        
        if response.status_code == 200:
            data = response.json()
            assert "targetId" in data
            assert data["targetId"] == 1
        elif response.status_code == 404:
            # Target might not exist, which is acceptable
            pytest.skip("Target ID 1 not found in database")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_target_interactions(self):
        """Test getting interactions for a target"""
        # Use a known target ID
        response = client.get("/targets/1/interactions")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            # If interactions exist, check structure
            if data:
                assert "targetId" in data[0]
                assert "ligandId" in data[0]
        elif response.status_code == 404:
            # Target might not exist
            pytest.skip("Target ID 1 not found in database")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_target_interactions_with_filters(self):
        """Test getting target interactions with filters"""
        response = client.get("/targets/1/interactions?species=Human&approved=true")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
        elif response.status_code == 404:
            pytest.skip("Target ID 1 not found in database")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_list_target_families(self):
        """Test listing target families"""
        response = client.get("/targets/families")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If families exist, check structure
        if data:
            assert "familyId" in data[0]
            assert "name" in data[0]
    
    def test_get_target_diseases(self):
        """Test getting diseases for a target"""
        response = client.get("/targets/1/diseases")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
        elif response.status_code == 404:
            pytest.skip("Target ID 1 not found in database")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

class TestLigandEndpoints:
    """Test ligand-related endpoints"""
    
    def test_list_ligands_no_filters(self):
        """Test listing ligands with no filters"""
        response = client.post("/ligands", json={})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_ligands_by_type(self):
        """Test filtering ligands by type"""
        response = client.post("/ligands", json={"type": "Synthetic organic"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that returned ligands are of correct type (if any returned)
        for ligand in data[:3]:  # Check first 3
            if "type" in ligand:
                assert ligand["type"] == "Synthetic organic"
    
    def test_list_ligands_by_approval_status(self):
        """Test filtering ligands by approval status"""
        response = client.post("/ligands", json={"approved": True})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that returned ligands are approved (if any returned)
        for ligand in data[:3]:  # Check first 3
            if "approved" in ligand:
                assert ligand["approved"] is True
    
    def test_list_ligands_by_name(self):
        """Test filtering ligands by name"""
        response = client.post("/ligands", json={"name": "serotonin"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that returned ligands contain the search term
        for ligand in data[:3]:  # Check first 3
            if "name" in ligand:
                assert "serotonin" in ligand["name"].lower()
    
    def test_get_single_ligand(self):
        """Test getting a single ligand by ID"""
        # Use a known ligand ID (5-HT)
        response = client.get("/ligands/1")
        
        if response.status_code == 200:
            data = response.json()
            assert "ligandId" in data
            assert data["ligandId"] == 1
        elif response.status_code == 404:
            # Ligand might not exist
            pytest.skip("Ligand ID 1 not found in database")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_ligand_interactions(self):
        """Test getting interactions for a ligand"""
        response = client.get("/ligands/1/interactions")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            # If interactions exist, check structure
            if data:
                assert "targetId" in data[0]
                assert "ligandId" in data[0]
        elif response.status_code == 404:
            pytest.skip("Ligand ID 1 not found in database")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

class TestInteractionEndpoints:
    """Test interaction-related endpoints"""
    
    def test_list_interactions_no_filters(self):
        """Test listing interactions with no filters"""
        response = client.post("/interactions", json={})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_interactions_by_target(self):
        """Test filtering interactions by target ID"""
        response = client.post("/interactions", json={"targetId": 1})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that returned interactions are for the correct target
        for interaction in data[:3]:  # Check first 3
            if "targetId" in interaction:
                assert interaction["targetId"] == 1
    
    def test_list_interactions_by_ligand(self):
        """Test filtering interactions by ligand ID"""
        response = client.post("/interactions", json={"ligandId": 1})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that returned interactions are for the correct ligand
        for interaction in data[:3]:  # Check first 3
            if "ligandId" in interaction:
                assert interaction["ligandId"] == 1
    
    def test_list_interactions_by_species(self):
        """Test filtering interactions by species"""
        response = client.post("/interactions", json={"species": "Human"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that returned interactions are for the correct species
        for interaction in data[:3]:  # Check first 3
            if "species" in interaction:
                assert interaction["species"] == "Human"
    
    def test_get_single_interaction(self):
        """Test getting a single interaction by ID"""
        response = client.get("/interactions/1")
        
        if response.status_code == 200:
            data = response.json()
            assert "interactionId" in data
            assert data["interactionId"] == 1
        elif response.status_code == 404:
            pytest.skip("Interaction ID 1 not found in database")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

class TestDiseaseEndpoints:
    """Test disease-related endpoints"""
    
    def test_list_diseases(self):
        """Test listing all diseases"""
        response = client.get("/diseases")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If diseases exist, check structure
        if data:
            assert "diseaseId" in data[0]
            assert "name" in data[0]
    
    def test_get_single_disease(self):
        """Test getting a single disease by ID"""
        response = client.get("/diseases/1")
        
        if response.status_code == 200:
            data = response.json()
            assert "diseaseId" in data
            assert data["diseaseId"] == 1
        elif response.status_code == 404:
            pytest.skip("Disease ID 1 not found in database")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_target_id(self):
        """Test handling of invalid target IDs"""
        response = client.get("/targets/999999")
        assert response.status_code in [404, 500]  # Either not found or server error
    
    def test_invalid_ligand_id(self):
        """Test handling of invalid ligand IDs"""
        response = client.get("/ligands/999999")
        assert response.status_code in [404, 500]
    
    def test_invalid_interaction_id(self):
        """Test handling of invalid interaction IDs"""
        response = client.get("/interactions/999999")
        assert response.status_code in [404, 500]
    
    def test_invalid_disease_id(self):
        """Test handling of invalid disease IDs"""
        response = client.get("/diseases/999999")
        assert response.status_code in [404, 500]
    
    def test_malformed_json_request(self):
        """Test handling of malformed JSON requests"""
        response = client.post("/targets", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422

class TestParametrizedEndpoints:
    """Test endpoints with various parameter combinations"""
    
    @pytest.mark.parametrize("target_type", ["GPCR", "Enzyme"])
    def test_target_types(self, target_type):
        """Test different target types"""
        response = client.post("/targets", json={"type": target_type})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.parametrize("ligand_type", ["Natural product"])
    def test_ligand_types(self, ligand_type):
        """Test different ligand types"""
        response = client.post("/ligands", json={"type": ligand_type})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.parametrize("species", ["Human", "Rat", "Mouse"])
    def test_species_filters(self, species):
        """Test different species filters"""
        response = client.post("/interactions", json={"species": species})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestResponseValidation:
    """Test response data validation and structure"""
    
    def test_target_response_structure(self):
        """Test that target responses have expected structure"""
        response = client.post("/targets", json={"type": "GPCR"})
        assert response.status_code == 200
        data = response.json()
        
        if data:  # If we have data
            target = data[0]
            # Check for expected fields (some may be None)
            expected_fields = ["targetId", "name", "abbreviation", "targetType"]
            for field in expected_fields:
                assert field in target or target.get(field) is not None
    
    def test_ligand_response_structure(self):
        """Test that ligand responses have expected structure"""
        response = client.post("/ligands", json={"approved": True})
        assert response.status_code == 200
        data = response.json()
        
        if data:  # If we have data
            ligand = data[0]
            # Check for expected fields
            expected_fields = ["ligandId", "name", "type"]
            for field in expected_fields:
                assert field in ligand or ligand.get(field) is not None
    
    def test_interaction_response_structure(self):
        """Test that interaction responses have expected structure"""
        response = client.post("/interactions", json={})
        assert response.status_code == 200
        data = response.json()
        
        if data:  # If we have data
            interaction = data[0]
            # Check for expected fields
            expected_fields = ["interactionId", "targetId", "ligandId"]
            for field in expected_fields:
                assert field in interaction or interaction.get(field) is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 