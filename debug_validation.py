import sys
sys.path.append('src')

import httpx
import asyncio
from pharmacology_mcp.pharmacology_api import LigandResponse

async def test_validation():
    # Get real data from the API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://www.guidetopharmacology.org/services/ligands", timeout=10)
            print(f"External API Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"External API returned {len(data)} ligands")
                
                if data:
                    first_ligand = data[0]
                    print(f"First ligand raw data: {first_ligand}")
                    
                    # Try to validate it
                    try:
                        validated = LigandResponse.model_validate(first_ligand)
                        print(f"Validation successful: {validated}")
                    except Exception as e:
                        print(f"Validation error: {e}")
                        print(f"Error type: {type(e)}")
                        
                        # Check what fields are missing or wrong
                        expected_fields = LigandResponse.model_fields.keys()
                        actual_fields = first_ligand.keys()
                        
                        print(f"Expected fields: {list(expected_fields)}")
                        print(f"Actual fields: {list(actual_fields)}")
                        print(f"Missing fields: {set(expected_fields) - set(actual_fields)}")
                        print(f"Extra fields: {set(actual_fields) - set(expected_fields)}")
                        
        except Exception as e:
            print(f"External API Error: {e}")

asyncio.run(test_validation()) 