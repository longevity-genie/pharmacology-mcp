import pytest
import asyncio
from pathlib import Path
import json
import tempfile
from unittest.mock import patch, Mock, AsyncMock
import httpx
from src.pharmacology_mcp.local import pharmacology_local_mcp

# Test fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.mark.asyncio
async def test_search_targets_to_file(temp_dir):
    """Test searching targets and saving to file"""
    output_file = Path(temp_dir) / "targets.json"
    
    # Mock the httpx response
    mock_response_data = [
        {
            "targetId": 1,
            "name": "5-HT1A receptor",
            "type": "GPCR"
        }
    ]
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # Call the tool function directly
        result = await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
            file_path_str=str(output_file),
            name="serotonin",
            target_type="GPCR"
        )
        
        # Verify the result
        assert result == str(output_file)
        assert output_file.exists()
        
        # Verify the file contents
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["targetId"] == 1
        assert data[0]["name"] == "5-HT1A receptor"

@pytest.mark.asyncio
async def test_search_ligands_to_file(temp_dir):
    """Test searching ligands and saving to file"""
    output_file = Path(temp_dir) / "ligands.json"
    
    # Mock the httpx response
    mock_response_data = [
        {
            "ligandId": 1,
            "name": "Serotonin",
            "type": "Endogenous peptide"
        }
    ]
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # Call the tool function directly
        result = await pharmacology_local_mcp._tool_manager._tools["search_ligands_to_file"].fn(
            file_path_str=str(output_file),
            name="serotonin",
            ligand_type="Endogenous peptide"
        )
        
        # Verify the result
        assert result == str(output_file)
        assert output_file.exists()
        
        # Verify the file contents
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["ligandId"] == 1
        assert data[0]["name"] == "Serotonin"

@pytest.mark.asyncio
async def test_get_target_interactions_to_file(temp_dir):
    """Test getting target interactions and saving to file"""
    output_file = Path(temp_dir) / "target_interactions.json"
    
    # Mock the httpx response
    mock_response_data = [
        {
            "interactionId": 1,
            "targetId": 1,
            "ligandId": 1,
            "species": "Human"
        }
    ]
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # Call the tool function directly
        result = await pharmacology_local_mcp._tool_manager._tools["get_target_interactions_to_file"].fn(
            target_id=1,
            file_path_str=str(output_file),
            species="Human"
        )
        
        # Verify the result
        assert result == str(output_file)
        assert output_file.exists()
        
        # Verify the file contents
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["targetId"] == 1
        assert data[0]["species"] == "Human"

@pytest.mark.asyncio
async def test_get_ligand_interactions_to_file(temp_dir):
    """Test getting ligand interactions and saving to file"""
    output_file = Path(temp_dir) / "ligand_interactions.json"
    
    # Mock the httpx response
    mock_response_data = [
        {
            "interactionId": 1,
            "targetId": 1,
            "ligandId": 1,
            "species": "Human"
        }
    ]
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # Call the tool function directly
        result = await pharmacology_local_mcp._tool_manager._tools["get_ligand_interactions_to_file"].fn(
            ligand_id=1,
            file_path_str=str(output_file),
            species="Human"
        )
        
        # Verify the result
        assert result == str(output_file)
        assert output_file.exists()
        
        # Verify the file contents
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["ligandId"] == 1
        assert data[0]["species"] == "Human"

@pytest.mark.asyncio
async def test_file_creation_with_nested_dirs(temp_dir):
    """Test that nested directories are created properly"""
    nested_path = Path(temp_dir) / "level1" / "level2" / "targets.json"
    
    # Mock the httpx response
    mock_response_data = [{"targetId": 1, "name": "Test Target"}]
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # Call the tool function directly
        result = await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
            file_path_str=str(nested_path)
        )
        
        # Verify the result
        assert result == str(nested_path)
        assert nested_path.exists()
        assert nested_path.parent.exists()
        assert nested_path.parent.parent.exists()

@pytest.mark.asyncio
async def test_error_handling_invalid_path():
    """Test error handling for invalid file paths"""
    # Try to write to a path that cannot be created
    invalid_path = "/root/cannot_write_here/test.json"
    
    # Mock the httpx response
    mock_response_data = [{"targetId": 1, "name": "Test Target"}]
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # This should raise an IOError
        with pytest.raises(IOError):
            await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
                file_path_str=invalid_path
            )

@pytest.mark.asyncio
async def test_api_error_handling(temp_dir):
    """Test handling of API errors"""
    output_file = Path(temp_dir) / "targets.json"
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response that raises an error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # This should raise an HTTPStatusError
        with pytest.raises(httpx.HTTPStatusError):
            await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
                file_path_str=str(output_file)
            )

@pytest.mark.asyncio
async def test_network_error_handling(temp_dir):
    """Test handling of network errors"""
    output_file = Path(temp_dir) / "targets.json"
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock client that raises a network error
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # This should raise a ConnectError
        with pytest.raises(httpx.ConnectError):
            await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
                file_path_str=str(output_file)
            )

@pytest.mark.asyncio
async def test_empty_response_handling(temp_dir):
    """Test handling of empty API responses"""
    output_file = Path(temp_dir) / "empty_targets.json"
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response with empty data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # Call the tool function directly
        result = await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
            file_path_str=str(output_file),
            name="nonexistent"
        )
        
        # Verify the result
        assert result == str(output_file)
        assert output_file.exists()
        
        # Verify the file contains empty list
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 0

@pytest.mark.asyncio
async def test_parameter_passing(temp_dir):
    """Test that parameters are correctly passed to the API"""
    output_file = Path(temp_dir) / "filtered_targets.json"
    
    # Mock the httpx response
    mock_response_data = [{"targetId": 1, "name": "Test Target", "type": "GPCR"}]
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()
        
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Set up the mock class to return our mock instance
        mock_client_class.return_value = mock_client
        
        # Call with multiple parameters
        result = await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
            file_path_str=str(output_file),
            name="adrenergic",
            target_type="GPCR",
            gene_symbol="ADRA1A",
            immuno=True,
            malaria=False
        )
        
        # Verify the call was made with correct parameters
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        
        # Check that params were passed correctly
        if len(call_args) > 1 and 'params' in call_args[1]:
            params = call_args[1]['params']
            assert params['name'] == 'adrenergic'
            assert params['type'] == 'GPCR'
            assert params['geneSymbol'] == 'ADRA1A'
            assert params['immuno'] == 'true'
            assert params['malaria'] == 'false'
        
        # Verify the result
        assert result == str(output_file)
        assert output_file.exists()

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 