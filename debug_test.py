import sys
sys.path.append('src')

from fastapi.testclient import TestClient
from pharmacology_mcp.pharmacology_api import PharmacologyRestAPI

# Create the app and test client
app = PharmacologyRestAPI()
client = TestClient(app)

# Test the failing endpoint
print("Testing POST /ligands with empty JSON...")
response = client.post("/ligands", json={})
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")

if response.status_code != 200:
    try:
        error_detail = response.json()
        print(f"Error Detail: {error_detail}")
    except:
        print("Could not parse error as JSON")

# Also test if the external API works directly
print("\nTesting external API directly...")
import httpx
import asyncio

async def test_external_api():
    async with httpx.AsyncClient() as external_client:
        try:
            response = await external_client.get("https://www.guidetopharmacology.org/services/ligands", timeout=10)
            print(f"External API Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"External API returned {len(data)} ligands")
                if data:
                    print(f"First ligand: {data[0]}")
        except Exception as e:
            print(f"External API Error: {e}")

asyncio.run(test_external_api()) 