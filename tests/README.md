# Pharmacology MCP Testing Suite

This testing suite is inspired by the excellent testing patterns from the pygtop library, providing comprehensive coverage of our pharmacology MCP server functionality.

## Test Organization

### Test Files

- **`test_pharmacology_api.py`** - Original integration tests that hit real API endpoints
- **`test_pharmacology_api_improved.py`** - Enhanced integration tests with better organization and validation
- **`test_pharmacology_mocked.py`** - Unit tests with comprehensive mocking (inspired by pygtop patterns)
- **`test_local.py`** - Tests for local MCP functionality
- **`conftest.py`** - Shared fixtures and test configuration
- **`pytest.ini`** - Pytest configuration and markers

### Test Categories

#### Integration Tests (`@pytest.mark.integration`)
- Test real API endpoints
- May be slow due to network calls
- Validate actual API responses
- Located in: `test_pharmacology_api.py`, `test_pharmacology_api_improved.py`

#### Unit Tests (`@pytest.mark.unit`)
- Fast tests with mocked external dependencies
- Test internal logic without network calls
- Comprehensive error handling validation
- Located in: `test_pharmacology_mocked.py`

#### API Tests (`@pytest.mark.api`)
- Focus on API endpoint functionality
- Both integration and unit variants available
- Cover all major endpoints: targets, ligands, interactions, diseases

#### Slow Tests (`@pytest.mark.slow`)
- Performance tests
- Large dataset handling
- Concurrent request testing
- Can be skipped with `-m "not slow"`

## Key Testing Patterns (Inspired by pygtop)

### 1. Comprehensive Mocking
```python
@patch('httpx.AsyncClient.get')
def test_list_targets_success(self, mock_get, mock_target_response):
    """Test successful target listing with mocked response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [mock_target_response]
    mock_get.return_value = mock_response
    
    response = client.post("/targets", json={"type": "GPCR"})
    assert response.status_code == 200
```

### 2. Fixture-Based Test Data
```python
@pytest.fixture
def sample_target_data():
    """Consistent test data across all tests"""
    return {
        "targetId": 1,
        "name": "5-HT<sub>1A</sub> receptor",
        "type": "GPCR"
    }
```

### 3. Parametrized Testing
```python
@pytest.mark.parametrize("target_type", ["GPCR", "Enzyme", "Ion channel"])
def test_target_types(self, target_type):
    """Test different target types"""
    response = client.post("/targets", json={"type": target_type})
    assert response.status_code == 200
```

### 4. Error Handling Validation
```python
@patch('httpx.AsyncClient.get')
def test_network_timeout_error(self, mock_get):
    """Test handling of network timeout errors"""
    mock_get.side_effect = httpx.TimeoutException("Request timed out")
    response = client.post("/targets", json={})
    assert response.status_code == 500
```

### 5. Data Structure Validation
```python
def assert_valid_target(target_data):
    """Validate target data structure"""
    required_fields = ["targetId", "name", "type"]
    for field in required_fields:
        assert field in target_data
    assert isinstance(target_data["targetId"], int)
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Only Unit Tests (Fast)
```bash
pytest -m unit
```

### Run Only Integration Tests
```bash
pytest -m integration
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

### Run Specific Test File
```bash
pytest tests/test_pharmacology_mocked.py
```

### Run with Coverage
```bash
pytest --cov=pharmacology_mcp --cov-report=html
```

### Run Tests in Parallel (if pytest-xdist installed)
```bash
pytest -n auto
```

## Test Structure Improvements

### From pygtop Patterns

1. **Organized Test Classes**: Each endpoint type has its own test class
2. **Comprehensive Fixtures**: Reusable test data and mock objects
3. **Error Scenario Coverage**: Network errors, malformed data, invalid parameters
4. **URL Construction Testing**: Verify correct API calls are made
5. **Response Processing Testing**: Handle various response formats
6. **Performance Testing**: Large datasets and concurrent requests

### Enhanced Features

1. **Automatic Test Marking**: Tests are automatically categorized based on file names
2. **Shared Utilities**: Common assertion functions for data validation
3. **Configurable Timeouts**: Prevent hanging tests
4. **Warning Filters**: Clean test output
5. **Async Support**: Proper handling of async operations

## Test Data Management

### Mock Data Consistency
All test files use the same fixture data from `conftest.py`, ensuring consistency across test suites.

### Realistic Test Data
Mock data reflects actual API response structures from the Guide to PHARMACOLOGY API.

### Edge Case Coverage
- Empty responses
- Malformed data
- Large datasets
- Network errors
- Invalid parameters

## Best Practices

### Writing New Tests

1. **Use Appropriate Markers**: Mark tests as `unit`, `integration`, `api`, or `slow`
2. **Leverage Fixtures**: Use shared fixtures from `conftest.py`
3. **Mock External Calls**: For unit tests, always mock HTTP requests
4. **Validate Data Structures**: Use assertion utilities for consistent validation
5. **Test Error Conditions**: Include negative test cases
6. **Document Test Purpose**: Clear docstrings explaining what each test validates

### Test Organization

1. **Group Related Tests**: Use test classes to organize related functionality
2. **Descriptive Names**: Test names should clearly indicate what they test
3. **Logical Ordering**: Arrange tests from simple to complex scenarios
4. **Separate Concerns**: Keep unit and integration tests in separate files

## Continuous Integration

The test suite is designed to work well in CI environments:

- Fast unit tests can run on every commit
- Integration tests can run on pull requests
- Slow tests can run nightly or on releases
- Proper error reporting and timeouts prevent hanging builds

## Dependencies

### Required
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client (for mocking)
- `fastapi[all]` - For TestClient

### Optional
- `pytest-cov` - Coverage reporting
- `pytest-xdist` - Parallel test execution
- `pytest-timeout` - Test timeouts
- `pytest-mock` - Enhanced mocking utilities

## Comparison with pygtop

Our testing approach adopts several key patterns from pygtop:

### Similarities
- Comprehensive mocking strategies
- Fixture-based test data
- Organized test classes
- Error handling validation
- Property testing patterns

### Enhancements
- Modern pytest features (markers, fixtures)
- FastAPI TestClient integration
- Async/await support
- Automatic test categorization
- Enhanced configuration management

This testing suite provides robust validation of our pharmacology MCP server while maintaining fast execution times and comprehensive coverage. 