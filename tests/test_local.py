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
        
        # Call the tool function directly
        result = await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
            file_path_str=str(output_file),
            name="test",
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

@pytest.mark.asyncio
async def test_api_error_handling(temp_dir):
    """Test handling of API errors"""
    output_file = Path(temp_dir) / "targets.json"
    
    with patch('src.pharmacology_mcp.local.httpx.AsyncClient') as mock_client_class:
        # Create mock client that raises an error
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPStatusError("Server Error", request=Mock(), response=Mock())
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        mock_client_class.return_value = mock_client
        
        # This should handle the error gracefully
        with pytest.raises(Exception):  # Expect some kind of error handling
            await pharmacology_local_mcp._tool_manager._tools["search_targets_to_file"].fn(
                file_path_str=str(output_file),
                name="test"
            )

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 