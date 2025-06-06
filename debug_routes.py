import sys
sys.path.append('src')

from fastapi.testclient import TestClient
from pharmacology_mcp.pharmacology_api import PharmacologyRestAPI

# Create the app and test client
app = PharmacologyRestAPI()
client = TestClient(app)

# Test the families endpoint specifically
print("Testing GET /targets/families...")
response = client.get("/targets/families")
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text[:500]}...")

if response.status_code != 200:
    try:
        error_detail = response.json()
        print(f"Error Detail: {error_detail}")
    except:
        print("Could not parse error as JSON")

# Test a simple target endpoint
print("\nTesting GET /targets/1...")
response = client.get("/targets/1")
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text[:200]}...")

# Test the ligands endpoint again but with more debugging
print("\nTesting POST /ligands again...")
response = client.post("/ligands", json={})
print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Text: {response.text}") 