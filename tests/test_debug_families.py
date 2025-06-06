import pytest
from fastapi.testclient import TestClient
from src.pharmacology_mcp.pharmacology_api import PharmacologyRestAPI

app = PharmacologyRestAPI()
client = TestClient(app)

def test_debug_families():
    """Debug test for families endpoint"""
    response = client.get("/targets/families")
    print(f"Status code: {response.status_code}")
    print(f"Response text: {response.text}")
    if response.status_code != 200:
        print(f"Response headers: {response.headers}")
    
    # Let's also test the actual external API
    import httpx
    import asyncio
    
    async def test_external():
        async with httpx.AsyncClient() as external_client:
            external_response = await external_client.get("https://www.guidetopharmacology.org/services/targets/families")
            print(f"External API status: {external_response.status_code}")
            if external_response.status_code == 200:
                data = external_response.json()
                print(f"External API returned {len(data)} families")
                if data:
                    print(f"First family: {data[0]}")
    
    asyncio.run(test_external())

if __name__ == "__main__":
    test_debug_families() 