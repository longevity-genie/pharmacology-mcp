"""
Pharmacology server class for use with just-agents BaseAgent.
Similar to OpenGenesMCP but for pharmacology tools.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import asyncio

from pharmacology_mcp.local import (
    search_targets_to_file as _search_targets_tool,
    search_ligands_to_file as _search_ligands_tool,
    get_target_interactions_to_file as _get_target_interactions_tool,
    get_ligand_interactions_to_file as _get_ligand_interactions_tool
)


class PharmacologyServer:
    """Pharmacology server that wraps MCP tools for use with just-agents."""
    
    def __init__(self):
        """Initialize the pharmacology server."""
        # Extract the actual callable functions from FastMCP FunctionTool objects
        self._search_targets_fn = _search_targets_tool.fn
        self._search_ligands_fn = _search_ligands_tool.fn
        self._get_target_interactions_fn = _get_target_interactions_tool.fn
        self._get_ligand_interactions_fn = _get_ligand_interactions_tool.fn
    
    def search_targets_to_file(
        self,
        filename: str,
        name: Optional[str] = None,
        target_type: Optional[str] = None,
        gene_symbol: Optional[str] = None,
        immuno: Optional[bool] = None,
        malaria: Optional[bool] = None
    ) -> str:
        """
        Search for pharmacological targets and save results to a file.
        
        Args:
            filename: Output filename for the results
            name: Target name to search for
            target_type: Type of target (e.g., 'GPCR', 'Ion channel')
            gene_symbol: Gene symbol to search for
            immuno: Include immunopharmacology data
            malaria: Include malaria data
            
        Returns:
            Status message about the search and file creation
        """
        return self._search_targets_fn(
            file_path_str=filename,
            name=name,
            target_type=target_type,
            gene_symbol=gene_symbol,
            immuno=immuno,
            malaria=malaria
        )
    
    def search_ligands_to_file(
        self,
        filename: str,
        name: Optional[str] = None,
        ligand_type: Optional[str] = None,
        inchikey: Optional[str] = None,
        approved: Optional[bool] = None,
        immuno: Optional[bool] = None,
        malaria: Optional[bool] = None,
        antibacterial: Optional[bool] = None
    ) -> str:
        """
        Search for pharmacological ligands and save results to a file.
        
        Args:
            filename: Output filename for the results
            name: Ligand name to search for
            ligand_type: Type of ligand (e.g., 'Small molecule', 'Antibody')
            inchikey: Search by InChIKey
            approved: Whether to filter for approved drugs
            immuno: Include immunopharmacology data
            malaria: Include malaria data
            antibacterial: Include antibacterial data
            
        Returns:
            Status message about the search and file creation
        """
        return self._search_ligands_fn(
            file_path_str=filename,
            name=name,
            ligand_type=ligand_type,
            inchikey=inchikey,
            approved=approved,
            immuno=immuno,
            malaria=malaria,
            antibacterial=antibacterial
        )
    
    def get_target_interactions_to_file(
        self,
        target_id: int,
        filename: str,
        species: Optional[str] = None,
        interaction_type: Optional[str] = None,
        approved_only: Optional[bool] = None
    ) -> str:
        """
        Get interactions for a specific target and save results to a file.
        
        Args:
            target_id: The target ID to get interactions for
            filename: Output filename for the results
            species: Filter by species (e.g., Human, Rat, Mouse)
            interaction_type: Filter by interaction type
            approved_only: Filter for approved ligands only
            
        Returns:
            Status message about the interaction retrieval and file creation
        """
        return self._get_target_interactions_fn(
            target_id=target_id,
            file_path_str=filename,
            species=species,
            interaction_type=interaction_type,
            approved_only=approved_only
        )
    
    def get_ligand_interactions_to_file(
        self,
        ligand_id: int,
        filename: str,
        species: Optional[str] = None,
        interaction_type: Optional[str] = None,
        primary_target_only: Optional[bool] = None
    ) -> str:
        """
        Get interactions for a specific ligand and save results to a file.
        
        Args:
            ligand_id: The ligand ID to get interactions for
            filename: Output filename for the results
            species: Filter by species (e.g., Human, Rat, Mouse)
            interaction_type: Filter by interaction type
            primary_target_only: Filter for primary targets only
            
        Returns:
            Status message about the interaction retrieval and file creation
        """
        return self._get_ligand_interactions_fn(
            ligand_id=ligand_id,
            file_path_str=filename,
            species=species,
            interaction_type=interaction_type,
            primary_target_only=primary_target_only
        ) 