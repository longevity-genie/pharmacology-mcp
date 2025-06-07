import asyncio
import httpx
import json

async def gather_test_data():
    base_url = 'https://www.guidetopharmacology.org/services'
    test_data = {}
    
    async with httpx.AsyncClient() as client:
        print('=== Gathering Test Data for Judged Tests ===')
        
        # 1. Get diverse targets
        print('\n1. Testing target searches...')
        target_searches = [
            {'name': 'dopamine', 'description': 'dopamine-related targets'},
            {'type': 'GPCR', 'description': 'GPCR targets'},
            {'type': 'Enzyme', 'description': 'enzyme targets'},
            {'geneSymbol': 'ADRA1A', 'description': 'specific gene symbol'},
        ]
        
        test_data['targets'] = {}
        for search in target_searches:
            params = {k: v for k, v in search.items() if k != 'description'}
            response = await client.get(f'{base_url}/targets', params=params)
            targets = response.json()
            test_data['targets'][search['description']] = {
                'query': params,
                'count': len(targets),
                'sample': targets[:3] if targets else []
            }
            print(f"  {search['description']}: {len(targets)} results")
        
        # 2. Get diverse ligands
        print('\n2. Testing ligand searches...')
        ligand_searches = [
            {'name': 'aspirin', 'description': 'aspirin-related ligands'},
            {'type': 'Synthetic organic', 'description': 'synthetic organic compounds'},
            {'approved': True, 'description': 'approved drugs'},
            {'name': 'morphine', 'description': 'morphine-related ligands'},
            {'antibacterial': True, 'description': 'antibacterial compounds'},
        ]
        
        test_data['ligands'] = {}
        for search in ligand_searches:
            params = {k: v for k, v in search.items() if k != 'description'}
            if 'approved' in params:
                params['approved'] = str(params['approved']).lower()
            if 'antibacterial' in params:
                params['antibacterial'] = str(params['antibacterial']).lower()
            response = await client.get(f'{base_url}/ligands', params=params)
            ligands = response.json()
            test_data['ligands'][search['description']] = {
                'query': params,
                'count': len(ligands),
                'sample': ligands[:3] if ligands else []
            }
            print(f"  {search['description']}: {len(ligands)} results")
        
        # 3. Get target families
        print('\n3. Testing target families...')
        response = await client.get(f'{base_url}/targets/families')
        families = response.json()
        test_data['families'] = {
            'count': len(families),
            'sample': families[:5] if families else []
        }
        print(f"  Found {len(families)} target families")
        
        # 4. Get interactions for specific targets
        print('\n4. Testing interactions...')
        test_data['interactions'] = {}
        
        # Get a specific target for interaction testing
        dopamine_targets = test_data['targets']['dopamine-related targets']['sample']
        if dopamine_targets:
            target_id = dopamine_targets[0]['targetId']
            response = await client.get(f'{base_url}/targets/{target_id}/interactions')
            interactions = response.json()
            test_data['interactions']['dopamine_target'] = {
                'target_id': target_id,
                'target_name': dopamine_targets[0]['name'],
                'count': len(interactions),
                'sample': interactions[:3] if interactions else []
            }
            print(f"  Target {target_id} interactions: {len(interactions)} results")
        
        # 5. Get ligand interactions
        aspirin_ligands = test_data['ligands']['aspirin-related ligands']['sample']
        if aspirin_ligands:
            ligand_id = aspirin_ligands[0]['ligandId']
            response = await client.get(f'{base_url}/ligands/{ligand_id}/interactions')
            interactions = response.json()
            test_data['interactions']['aspirin_ligand'] = {
                'ligand_id': ligand_id,
                'ligand_name': aspirin_ligands[0]['name'],
                'count': len(interactions),
                'sample': interactions[:3] if interactions else []
            }
            print(f"  Ligand {ligand_id} interactions: {len(interactions)} results")
        
        # 6. Get diseases
        print('\n5. Testing diseases...')
        response = await client.get(f'{base_url}/diseases')
        diseases = response.json()
        test_data['diseases'] = {
            'count': len(diseases),
            'sample': diseases[:5] if diseases else []
        }
        print(f"  Found {len(diseases)} diseases")
        
        # 7. Get specific target details
        print('\n6. Testing specific target details...')
        if dopamine_targets:
            target_id = dopamine_targets[0]['targetId']
            response = await client.get(f'{base_url}/targets/{target_id}')
            target_detail = response.json()
            test_data['target_details'] = {
                'target_id': target_id,
                'details': target_detail
            }
            print(f"  Got details for target {target_id}")
        
        # 8. Get specific ligand details
        print('\n7. Testing specific ligand details...')
        if aspirin_ligands:
            ligand_id = aspirin_ligands[0]['ligandId']
            response = await client.get(f'{base_url}/ligands/{ligand_id}')
            ligand_detail = response.json()
            test_data['ligand_details'] = {
                'ligand_id': ligand_id,
                'details': ligand_detail
            }
            print(f"  Got details for ligand {ligand_id}")
    
    # Save test data
    with open('test_data_for_judged_tests.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f'\n=== Test Data Summary ===')
    print(f"Targets: {sum(data['count'] for data in test_data['targets'].values())} total across searches")
    print(f"Ligands: {sum(data['count'] for data in test_data['ligands'].values())} total across searches")
    print(f"Families: {test_data['families']['count']}")
    print(f"Diseases: {test_data['diseases']['count']}")
    print(f"Saved comprehensive test data to test_data_for_judged_tests.json")
    
    return test_data

if __name__ == "__main__":
    asyncio.run(gather_test_data()) 