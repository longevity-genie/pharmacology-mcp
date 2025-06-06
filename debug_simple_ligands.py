import sys
sys.path.append('src')

import httpx
import asyncio
from typing import List
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pharmacology_mcp.pharmacology_api import LigandResponse, LigandQueryRequest

# Create a simple FastAPI app with just the ligands endpoint
app = FastAPI()

BASE_URL = "https://www.guidetopharmacology.org/services"

@app.post("/ligands", response_model=List[LigandResponse])
async def list_ligands_simple(request: LigandQueryRequest):
    """Simplified ligands endpoint without eliot logging"""
    try:
        params = {k: v for k, v in request.model_dump().items() if v is not None}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/ligands", params=params)
            response.raise_for_status()
            
        data = response.json()
        if not isinstance(data, list):
            return []
        
        validated_ligands = []
        for ligand_data in data:
            try:
                validated_ligands.append(LigandResponse.model_validate(ligand_data))
            except Exception as e:
                print(f"Validation error for ligand: {e}")
                pass
        
        return validated_ligands
    except Exception as e:
        print(f"Error in list_ligands_simple: {e}")
        raise

# Test the simplified endpoint
client = TestClient(app)

print("Testing simplified POST /ligands...")
response = client.post("/ligands", json={})
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text[:200]}...")

if response.status_code == 200:
    data = response.json()
    print(f"Success! Got {len(data)} ligands")
else:
    try:
        error_detail = response.json()
        print(f"Error Detail: {error_detail}")
    except:
        print("Could not parse error as JSON") 