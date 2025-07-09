import asyncio
import httpx
import json
import pytest

@pytest.mark.asyncio
async def test_api():
    base_url = 'https://www.guidetopharmacology.org/services'
    
    # Test targets search
    async with httpx.AsyncClient() as client:
        print('=== Testing Targets API ===')
        response = await client.get(f'{base_url}/targets', params={'name': 'dopamine'})
        targets = response.json()
        print(f'Found {len(targets)} targets with dopamine in name')
        if targets:
            print(f'First target: {targets[0]}')
        
        print('\n=== Testing Ligands API ===')
        response = await client.get(f'{base_url}/ligands', params={'name': 'aspirin'})
        ligands = response.json()
        print(f'Found {len(ligands)} ligands with aspirin in name')
        if ligands:
            print(f'First ligand: {ligands[0]}')
            
        print('\n=== Testing Target Families ===')
        response = await client.get(f'{base_url}/targets/families')
        families = response.json()
        print(f'Found {len(families)} target families')
        if families:
            print(f'First family: {families[0]}')
            
        print('\n=== Testing Interactions ===')
        if targets:
            target_id = targets[0].get('targetId')
            if target_id:
                response = await client.get(f'{base_url}/targets/{target_id}/interactions')
                interactions = response.json()
                print(f'Found {len(interactions)} interactions for target {target_id}')
                if interactions:
                    print(f'First interaction: {interactions[0]}')

if __name__ == "__main__":
    asyncio.run(test_api()) 