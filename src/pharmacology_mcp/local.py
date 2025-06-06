import asyncio
from fastmcp import FastMCP, Client
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
import json

# Define subserver
pharmacology_local_mcp = FastMCP(name="PharmacologyLocalService")

@pharmacology_local_mcp.tool(
    name="search_targets_to_file",
    description="Search for pharmacological targets and save results to a file",
    tags={"targets", "search", "file"}
)
async def search_targets_to_file(
    file_path_str: str,
    name: Optional[str] = None,
    target_type: Optional[str] = None,
    gene_symbol: Optional[str] = None,
    immuno: Optional[bool] = None,
    malaria: Optional[bool] = None
) -> str:
    """
    Search for pharmacological targets and save results to a file.
    
    Args:
        file_path_str: The full path where the results should be saved
        name: Search by target name (partial match)
        target_type: Filter by target type (e.g., GPCR, Enzyme, Ion channel)
        gene_symbol: Search by gene symbol
        immuno: Include immunopharmacology data
        malaria: Include malaria data
        
    Returns:
        The string representation of the path to the saved file
    """
    file_path = Path(file_path_str)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"Could not create parent directory for {file_path}: {str(e)}") from e
    
    # Build query parameters
    params = {}
    if name:
        params['name'] = name
    if target_type:
        params['type'] = target_type
    if gene_symbol:
        params['geneSymbol'] = gene_symbol
    if immuno is not None:
        params['immuno'] = str(immuno).lower()
    if malaria is not None:
        params['malaria'] = str(malaria).lower()
    
    # Make the API request
    base_url = "https://www.guidetopharmacology.org/services"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/targets", params=params)
        response.raise_for_status()
        
    data = response.json()
    
    # Save to file
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        raise IOError(f"Failed to write results to {file_path}: {str(e)}") from e
    
    return str(file_path)

@pharmacology_local_mcp.tool(
    name="search_ligands_to_file",
    description="Search for ligands/compounds and save results to a file",
    tags={"ligands", "search", "file"}
)
async def search_ligands_to_file(
    file_path_str: str,
    name: Optional[str] = None,
    ligand_type: Optional[str] = None,
    inchikey: Optional[str] = None,
    approved: Optional[bool] = None,
    immuno: Optional[bool] = None,
    malaria: Optional[bool] = None,
    antibacterial: Optional[bool] = None
) -> str:
    """
    Search for ligands/compounds and save results to a file.
    
    Args:
        file_path_str: The full path where the results should be saved
        name: Search by ligand name (partial match)
        ligand_type: Filter by ligand type (e.g., Synthetic organic, Metabolite, Natural product, Peptide)
        inchikey: Search by InChIKey
        approved: Filter for approved drugs only
        immuno: Include immunopharmacology data
        malaria: Include malaria data
        antibacterial: Include antibacterial data
        
    Returns:
        The string representation of the path to the saved file
    """
    file_path = Path(file_path_str)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"Could not create parent directory for {file_path}: {str(e)}") from e
    
    # Build query parameters
    params = {}
    if name:
        params['name'] = name
    if ligand_type:
        params['type'] = ligand_type
    if inchikey:
        params['inchikey'] = inchikey
    if approved is not None:
        params['approved'] = str(approved).lower()
    if immuno is not None:
        params['immuno'] = str(immuno).lower()
    if malaria is not None:
        params['malaria'] = str(malaria).lower()
    if antibacterial is not None:
        params['antibacterial'] = str(antibacterial).lower()
    
    # Make the API request
    base_url = "https://www.guidetopharmacology.org/services"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/ligands", params=params)
        response.raise_for_status()
        
    data = response.json()
    
    # Save to file
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        raise IOError(f"Failed to write results to {file_path}: {str(e)}") from e
    
    return str(file_path)

@pharmacology_local_mcp.tool(
    name="get_target_interactions_to_file",
    description="Get all interactions for a specific target and save to a file",
    tags={"targets", "interactions", "file"}
)
async def get_target_interactions_to_file(
    target_id: int,
    file_path_str: str,
    species: Optional[str] = None,
    interaction_type: Optional[str] = None,
    approved_only: Optional[bool] = None
) -> str:
    """
    Get all interactions for a specific target and save to a file.
    
    Args:
        target_id: The target ID
        file_path_str: The full path where the results should be saved
        species: Filter by species (e.g., Human, Rat, Mouse)
        interaction_type: Filter by interaction type
        approved_only: Filter for approved ligands only
        
    Returns:
        The string representation of the path to the saved file
    """
    file_path = Path(file_path_str)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"Could not create parent directory for {file_path}: {str(e)}") from e
    
    # Build query parameters
    params = {}
    if species:
        params['species'] = species
    if interaction_type:
        params['type'] = interaction_type
    if approved_only is not None:
        params['approved'] = str(approved_only).lower()
    
    # Make the API request
    base_url = "https://www.guidetopharmacology.org/services"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/targets/{target_id}/interactions", params=params)
        response.raise_for_status()
        
    data = response.json()
    
    # Save to file
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        raise IOError(f"Failed to write results to {file_path}: {str(e)}") from e
    
    return str(file_path)

@pharmacology_local_mcp.tool(
    name="get_ligand_interactions_to_file",
    description="Get all interactions for a specific ligand and save to a file",
    tags={"ligands", "interactions", "file"}
)
async def get_ligand_interactions_to_file(
    ligand_id: int,
    file_path_str: str,
    species: Optional[str] = None,
    interaction_type: Optional[str] = None,
    primary_target_only: Optional[bool] = None
) -> str:
    """
    Get all interactions for a specific ligand and save to a file.
    
    Args:
        ligand_id: The ligand ID
        file_path_str: The full path where the results should be saved
        species: Filter by species (e.g., Human, Rat, Mouse)
        interaction_type: Filter by interaction type
        primary_target_only: Filter for primary targets only
        
    Returns:
        The string representation of the path to the saved file
    """
    file_path = Path(file_path_str)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"Could not create parent directory for {file_path}: {str(e)}") from e
    
    # Build query parameters
    params = {}
    if species:
        params['species'] = species
    if interaction_type:
        params['type'] = interaction_type
    if primary_target_only is not None:
        params['primaryTarget'] = str(primary_target_only).lower()
    
    # Make the API request
    base_url = "https://www.guidetopharmacology.org/services"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/ligands/{ligand_id}/interactions", params=params)
        response.raise_for_status()
        
    data = response.json()
    
    # Save to file
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        raise IOError(f"Failed to write results to {file_path}: {str(e)}") from e
    
    return str(file_path) 