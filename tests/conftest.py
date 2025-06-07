import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, mocked)"
    )

# Essential fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup after test
    shutil.rmtree(temp_path)

@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response object"""
    def _create_response(status_code=200, json_data=None, text=""):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = text
        if json_data is not None:
            mock_response.json.return_value = json_data
        return mock_response
    return _create_response 