from typing import Optional, List, Dict, Any, Union
import httpx
from pydantic import BaseModel, Field, ConfigDict
from fastapi import FastAPI, Path as FastApiPath, HTTPException, Query
from fastapi.responses import RedirectResponse
from eliot import start_action

# Base URL for Guide to PHARMACOLOGY API
BASE_URL = "https://www.guidetopharmacology.org/services"

# Response Models
class TargetResponse(BaseModel):
    """Response model for target information"""
    model_config = ConfigDict(extra='allow')
    
    targetId: Optional[int] = Field(None, description="Target identifier")
    name: Optional[str] = Field(None, description="Target name")
    abbreviation: Optional[str] = Field(None, description="Target abbreviation")
    systematicName: Optional[str] = Field(None, description="Systematic name")
    type: Optional[str] = Field(None, description="Target type")  # Changed from targetType
    familyIds: Optional[List[int]] = Field(None, description="Family IDs")
    subunitIds: Optional[List[int]] = Field(None, description="Subunit IDs")
    complexIds: Optional[List[int]] = Field(None, description="Complex IDs")
    
    # Add backward compatibility property
    @property
    def targetType(self) -> Optional[str]:
        """Backward compatibility property for targetType"""
        return self.type

class LigandResponse(BaseModel):
    """Response model for ligand information"""
    model_config = ConfigDict(extra='allow')
    
    ligandId: Optional[int] = Field(None, description="Ligand identifier")
    name: Optional[str] = Field(None, description="Ligand name")
    abbreviation: Optional[str] = Field(None, description="Ligand abbreviation")
    inn: Optional[str] = Field(None, description="INN name")  # Changed from innOrIupacName
    type: Optional[str] = Field(None, description="Ligand type")
    species: Optional[str] = Field(None, description="Species")
    radioactive: Optional[bool] = Field(None, description="Is radioactive")
    labelled: Optional[bool] = Field(None, description="Is labelled")
    approved: Optional[bool] = Field(None, description="Is approved")
    withdrawn: Optional[bool] = Field(None, description="Is withdrawn")
    whoEssential: Optional[bool] = Field(None, description="WHO essential medicine")
    immuno: Optional[bool] = Field(None, description="Immunopharmacology")
    malaria: Optional[bool] = Field(None, description="Malaria")
    antibacterial: Optional[bool] = Field(None, description="Antibacterial")
    approvalSource: Optional[str] = Field(None, description="Approval source")
    subunitIds: Optional[List[int]] = Field(None, description="Subunit IDs")
    complexIds: Optional[List[int]] = Field(None, description="Complex IDs")
    prodrugIds: Optional[List[int]] = Field(None, description="Prodrug IDs")
    activeDrugIds: Optional[List[int]] = Field(None, description="Active drug IDs")
    
    # Add backward compatibility property
    @property
    def innOrIupacName(self) -> Optional[str]:
        """Backward compatibility property for innOrIupacName"""
        return self.inn

class InteractionResponse(BaseModel):
    """Response model for interaction information"""
    model_config = ConfigDict(extra='allow')
    
    interactionId: Optional[int] = Field(None, description="Interaction identifier")
    targetId: Optional[int] = Field(None, description="Target ID")
    ligandId: Optional[int] = Field(None, description="Ligand ID")
    targetName: Optional[str] = Field(None, description="Target name")
    ligandName: Optional[str] = Field(None, description="Ligand name")
    type: Optional[str] = Field(None, description="Interaction type")
    action: Optional[str] = Field(None, description="Action")
    actionComment: Optional[str] = Field(None, description="Action comment")
    selectivity: Optional[str] = Field(None, description="Selectivity")
    endogenous: Optional[bool] = Field(None, description="Is endogenous")
    species: Optional[str] = Field(None, description="Species")
    primaryTarget: Optional[bool] = Field(None, description="Is primary target")
    concentration: Optional[str] = Field(None, description="Concentration")
    concentrationRange: Optional[str] = Field(None, description="Concentration range")
    affinity: Optional[str] = Field(None, description="Affinity")
    affinityType: Optional[str] = Field(None, description="Affinity type")

class FamilyResponse(BaseModel):
    """Response model for family information"""
    model_config = ConfigDict(extra='allow')
    
    familyId: Optional[int] = Field(None, description="Family identifier")
    name: Optional[str] = Field(None, description="Family name")
    parentFamilyIds: Optional[List[int]] = Field(None, description="Parent family IDs")
    subFamilyIds: Optional[List[int]] = Field(None, description="Sub family IDs")
    targetIds: Optional[List[int]] = Field(None, description="Target IDs in family")
    
    # Add backward compatibility property
    @property
    def parentFamilyId(self) -> Optional[int]:
        """Backward compatibility property for parentFamilyId"""
        return self.parentFamilyIds[0] if self.parentFamilyIds else None

class DiseaseResponse(BaseModel):
    """Response model for disease information"""
    model_config = ConfigDict(extra='allow')
    
    diseaseId: Optional[int] = Field(None, description="Disease identifier")
    name: Optional[str] = Field(None, description="Disease name")
    description: Optional[str] = Field(None, description="Disease description")
    synonyms: Optional[List[str]] = Field(None, description="Disease synonyms")

# Request Models
class TargetQueryRequest(BaseModel):
    type: Optional[str] = Field(None, description="Target type filter")
    name: Optional[str] = Field(None, description="Search by name")
    geneSymbol: Optional[str] = Field(None, description="Search by gene symbol")
    ecNumber: Optional[str] = Field(None, description="Search by EC number")
    accession: Optional[str] = Field(None, description="External database accession")
    database: Optional[str] = Field(None, description="External database name")
    immuno: Optional[bool] = Field(None, description="Include immunopharmacology data")
    malaria: Optional[bool] = Field(None, description="Include malaria data")

class LigandQueryRequest(BaseModel):
    type: Optional[str] = Field(None, description="Ligand type filter")
    name: Optional[str] = Field(None, description="Search by name")
    geneSymbol: Optional[str] = Field(None, description="Search by gene symbol")
    accession: Optional[str] = Field(None, description="External database accession")
    database: Optional[str] = Field(None, description="External database name")
    inchikey: Optional[str] = Field(None, description="InChIKey")
    immuno: Optional[bool] = Field(None, description="Include immunopharmacology data")
    malaria: Optional[bool] = Field(None, description="Include malaria data")
    antibacterial: Optional[bool] = Field(None, description="Include antibacterial data")
    approved: Optional[bool] = Field(None, description="Filter by approval status")
    molWeightGt: Optional[float] = Field(None, description="Minimum molecular weight")
    molWeightLt: Optional[float] = Field(None, description="Maximum molecular weight")

class InteractionQueryRequest(BaseModel):
    targetId: Optional[int] = Field(None, description="Filter by target ID")
    ligandId: Optional[int] = Field(None, description="Filter by ligand ID")
    type: Optional[str] = Field(None, description="Interaction type")
    affinityType: Optional[str] = Field(None, description="Affinity type")
    species: Optional[str] = Field(None, description="Species")
    affinity: Optional[str] = Field(None, description="Affinity value")
    ligandType: Optional[str] = Field(None, description="Ligand type")
    approved: Optional[bool] = Field(None, description="Is approved")
    primaryTarget: Optional[bool] = Field(None, description="Is primary target")

# Mixin classes for different API endpoints
class TargetRoutesMixin:
    def _target_routes_config(self):
        """Configure target routes for the API"""

        @self.post(
            "/targets",
            response_model=List[TargetResponse],
            tags=["targets"],
            summary="List targets with optional filters",
            operation_id="list_targets",
            description="""
            Retrieve a list of targets from the Guide to PHARMACOLOGY database.
            
            You can filter targets by:
            - Type (e.g., GPCR, Enzyme, Ion channel)
            - Name (partial match)
            - Gene symbol
            - EC number (for enzymes)
            - External database accession
            - Special categories (immuno, malaria)
            """)
        async def list_targets(request: TargetQueryRequest):
            """List targets with optional filters"""
            with start_action(action_type="api:list_targets") as action:
                params = {k: v for k, v in request.model_dump().items() if v is not None}
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{BASE_URL}/targets", params=params)
                    response.raise_for_status()
                    
                data = response.json()
                if not isinstance(data, list):
                    return []
                
                validated_targets = []
                for target_data in data:
                    try:
                        validated_targets.append(TargetResponse.model_validate(target_data))
                    except Exception as e:
                        action.log(message_type="warning:target_validation_error", error=str(e))
                        pass
                
                return validated_targets

        @self.get(
            "/targets/families",
            response_model=List[FamilyResponse],
            tags=["targets"],
            summary="List target families",
            operation_id="list_target_families",
            description="Retrieve a list of all target families.")
        async def list_target_families(
            family_type: Optional[str] = Query(None, alias="type", description="Family type filter"),
            name: Optional[str] = Query(None, description="Search by family name")
        ):
            """List target families"""
            with start_action(action_type="api:list_target_families") as action:
                try:
                    params = {}
                    if family_type:
                        params['type'] = family_type
                    if name:
                        params['name'] = name
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{BASE_URL}/targets/families", params=params)
                        response.raise_for_status()
                        
                    data = response.json()
                    if not isinstance(data, list):
                        return []
                    
                    validated_families = []
                    for family_data in data:
                        try:
                            validated_families.append(FamilyResponse.model_validate(family_data))
                        except Exception as e:
                            action.log(message_type="warning:family_validation_error", error=str(e))
                            pass
                    
                    return validated_families
                except httpx.HTTPStatusError as e:
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:list_target_families", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

        @self.get(
            "/targets/{targetId}",
            response_model=TargetResponse,
            tags=["targets"],
            summary="Get a single target by ID",
            operation_id="get_target",
            description="Retrieve detailed information about a specific target by its ID.")
        async def get_target(
            targetId: int = FastApiPath(..., description="Target identifier")
        ):
            """Get target information by ID"""
            with start_action(action_type="api:get_target", target_id=targetId) as action:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(f"{BASE_URL}/targets/{targetId}")
                        response.raise_for_status()
                        
                    data = response.json()
                    return TargetResponse.model_validate(data)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        raise HTTPException(status_code=404, detail=f"Target {targetId} not found")
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:get_target", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

        @self.get(
            "/targets/{targetId}/interactions",
            response_model=List[InteractionResponse],
            tags=["targets"],
            summary="Get interactions for a target",
            operation_id="get_target_interactions",
            description="Retrieve all interactions for a specific target.")
        async def get_target_interactions(
            targetId: int = FastApiPath(..., description="Target identifier"),
            type: Optional[str] = Query(None, description="Interaction type filter"),
            species: Optional[str] = Query(None, description="Species filter"),
            approved: Optional[bool] = Query(None, description="Filter by approved ligands")
        ):
            """Get interactions for a specific target"""
            with start_action(action_type="api:get_target_interactions", target_id=targetId) as action:
                try:
                    params = {}
                    if type:
                        params['type'] = type
                    if species:
                        params['species'] = species
                    if approved is not None:
                        params['approved'] = str(approved).lower()
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{BASE_URL}/targets/{targetId}/interactions", params=params)
                        response.raise_for_status()
                        
                    data = response.json()
                    if not isinstance(data, list):
                        return []
                    
                    validated_interactions = []
                    for interaction_data in data:
                        try:
                            validated_interactions.append(InteractionResponse.model_validate(interaction_data))
                        except Exception as e:
                            action.log(message_type="warning:interaction_validation_error", error=str(e))
                            pass
                    
                    return validated_interactions
                except httpx.HTTPStatusError as e:
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:get_target_interactions", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

        @self.get(
            "/targets/{targetId}/diseases",
            response_model=List[DiseaseResponse],
            tags=["targets"],
            summary="Get diseases associated with a target",
            operation_id="get_target_diseases",
            description="Retrieve diseases associated with a specific target.")
        async def get_target_diseases(
            targetId: int = FastApiPath(..., description="Target identifier")
        ):
            """Get diseases for a specific target"""
            with start_action(action_type="api:get_target_diseases", target_id=targetId) as action:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{BASE_URL}/targets/{targetId}/diseases")
                        response.raise_for_status()
                        
                    data = response.json()
                    if not isinstance(data, list):
                        return []
                    
                    validated_diseases = []
                    for disease_data in data:
                        try:
                            validated_diseases.append(DiseaseResponse.model_validate(disease_data))
                        except Exception as e:
                            action.log(message_type="warning:disease_validation_error", error=str(e))
                            pass
                    
                    return validated_diseases
                except httpx.HTTPStatusError as e:
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:get_target_diseases", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

class LigandRoutesMixin:
    def _ligand_routes_config(self):
        """Configure ligand routes for the API"""

        @self.post(
            "/ligands",
            response_model=List[LigandResponse],
            tags=["ligands"],
            summary="List ligands with optional filters",
            operation_id="list_ligands",
            description="""
            Retrieve a list of ligands from the Guide to PHARMACOLOGY database.
            
            You can filter ligands by:
            - Type (e.g., Synthetic organic, Metabolite, Natural product, Peptide)
            - Name (partial match)
            - Gene symbol (for peptide ligands)
            - InChIKey
            - External database accession
            - Special categories (immuno, malaria, antibacterial)
            - Physicochemical properties (molecular weight, LogP, etc.)
            """)
        async def list_ligands(request: LigandQueryRequest):
            """List ligands with optional filters"""
            with start_action(action_type="api:list_ligands") as action:
                params = {k: v for k, v in request.model_dump().items() if v is not None}
                
                async with httpx.AsyncClient(timeout=30.0) as client:
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
                        action.log(message_type="warning:ligand_validation_error", error=str(e))
                        pass
                
                return validated_ligands

        @self.get(
            "/ligands/{ligandId}",
            response_model=LigandResponse,
            tags=["ligands"],
            summary="Get a single ligand by ID",
            operation_id="get_ligand",
            description="Retrieve detailed information about a specific ligand by its ID.")
        async def get_ligand(
            ligandId: int = FastApiPath(..., description="Ligand identifier")
        ):
            """Get ligand information by ID"""
            with start_action(action_type="api:get_ligand", ligand_id=ligandId) as action:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(f"{BASE_URL}/ligands/{ligandId}")
                        response.raise_for_status()
                        
                    data = response.json()
                    return LigandResponse.model_validate(data)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        raise HTTPException(status_code=404, detail=f"Ligand {ligandId} not found")
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:get_ligand", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

        @self.get(
            "/ligands/{ligandId}/interactions",
            response_model=List[InteractionResponse],
            tags=["ligands"],
            summary="Get interactions for a ligand",
            operation_id="get_ligand_interactions",
            description="Retrieve all interactions for a specific ligand.")
        async def get_ligand_interactions(
            ligandId: int = FastApiPath(..., description="Ligand identifier"),
            type: Optional[str] = Query(None, description="Interaction type filter"),
            species: Optional[str] = Query(None, description="Species filter"),
            primaryTarget: Optional[bool] = Query(None, description="Filter by primary target")
        ):
            """Get interactions for a specific ligand"""
            with start_action(action_type="api:get_ligand_interactions", ligand_id=ligandId) as action:
                try:
                    params = {}
                    if type:
                        params['type'] = type
                    if species:
                        params['species'] = species
                    if primaryTarget is not None:
                        params['primaryTarget'] = str(primaryTarget).lower()
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{BASE_URL}/ligands/{ligandId}/interactions", params=params)
                        response.raise_for_status()
                        
                    data = response.json()
                    if not isinstance(data, list):
                        return []
                    
                    validated_interactions = []
                    for interaction_data in data:
                        try:
                            validated_interactions.append(InteractionResponse.model_validate(interaction_data))
                        except Exception as e:
                            action.log(message_type="warning:interaction_validation_error", error=str(e))
                            pass
                    
                    return validated_interactions
                except httpx.HTTPStatusError as e:
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:get_ligand_interactions", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

class InteractionRoutesMixin:
    def _interaction_routes_config(self):
        """Configure interaction routes for the API"""

        @self.post(
            "/interactions",
            response_model=List[InteractionResponse],
            tags=["interactions"],
            summary="List interactions with optional filters",
            operation_id="list_interactions",
            description="""
            Retrieve a list of interactions from the Guide to PHARMACOLOGY database.
            
            You can filter interactions by:
            - Target ID
            - Ligand ID
            - Interaction type
            - Affinity type and value
            - Species
            - Approved/primary target status
            """)
        async def list_interactions(request: InteractionQueryRequest):
            """List interactions with optional filters"""
            with start_action(action_type="api:list_interactions") as action:
                params = {k: v for k, v in request.model_dump().items() if v is not None}
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{BASE_URL}/interactions", params=params)
                    response.raise_for_status()
                    
                data = response.json()
                if not isinstance(data, list):
                    return []
                
                validated_interactions = []
                for interaction_data in data:
                    try:
                        validated_interactions.append(InteractionResponse.model_validate(interaction_data))
                    except Exception as e:
                        action.log(message_type="warning:interaction_validation_error", error=str(e))
                        pass
                
                return validated_interactions

        @self.get(
            "/interactions/{interactionId}",
            response_model=InteractionResponse,
            tags=["interactions"],
            summary="Get a single interaction by ID",
            operation_id="get_interaction",
            description="Retrieve detailed information about a specific interaction by its ID.")
        async def get_interaction(
            interactionId: int = FastApiPath(..., description="Interaction identifier")
        ):
            """Get interaction information by ID"""
            with start_action(action_type="api:get_interaction", interaction_id=interactionId) as action:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{BASE_URL}/interactions/{interactionId}")
                        response.raise_for_status()
                        
                    data = response.json()
                    return InteractionResponse.model_validate(data)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        raise HTTPException(status_code=404, detail=f"Interaction {interactionId} not found")
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:get_interaction", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

class DiseaseRoutesMixin:
    def _disease_routes_config(self):
        """Configure disease routes for the API"""

        @self.get(
            "/diseases",
            response_model=List[DiseaseResponse],
            tags=["diseases"],
            summary="List all diseases",
            operation_id="list_diseases",
            description="Retrieve a list of all diseases in the database.")
        async def list_diseases():
            """List all diseases"""
            with start_action(action_type="api:list_diseases") as action:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{BASE_URL}/diseases")
                        response.raise_for_status()
                        
                    data = response.json()
                    if not isinstance(data, list):
                        return []
                    
                    validated_diseases = []
                    for disease_data in data:
                        try:
                            validated_diseases.append(DiseaseResponse.model_validate(disease_data))
                        except Exception as e:
                            action.log(message_type="warning:disease_validation_error", error=str(e))
                            pass
                    
                    return validated_diseases
                except httpx.HTTPStatusError as e:
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:list_diseases", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

        @self.get(
            "/diseases/{diseaseId}",
            response_model=DiseaseResponse,
            tags=["diseases"],
            summary="Get a single disease by ID",
            operation_id="get_disease",
            description="Retrieve detailed information about a specific disease by its ID.")
        async def get_disease(
            diseaseId: int = FastApiPath(..., description="Disease identifier")
        ):
            """Get disease information by ID"""
            with start_action(action_type="api:get_disease", disease_id=diseaseId) as action:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{BASE_URL}/diseases/{diseaseId}")
                        response.raise_for_status()
                        
                    data = response.json()
                    return DiseaseResponse.model_validate(data)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        raise HTTPException(status_code=404, detail=f"Disease {diseaseId} not found")
                    raise HTTPException(status_code=e.response.status_code, detail=str(e))
                except Exception as e:
                    action.log(message_type="error:get_disease", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))

class PharmacologyRestAPI(FastAPI, TargetRoutesMixin, LigandRoutesMixin, InteractionRoutesMixin, DiseaseRoutesMixin):
    """
    Main FastAPI application for the Guide to PHARMACOLOGY MCP Server.
    """
    
    def __init__(
        self,
        *,
        debug: bool = False,
        title: str = "Guide to PHARMACOLOGY MCP Server",
        description: str = "MCP Server for the Guide to PHARMACOLOGY database, providing access to pharmacological data including targets, ligands, and interactions",
        version: str = "0.1.0",
        openapi_url: str = "/openapi.json",
        openapi_tags: Optional[List[Dict[str, Any]]] = None,
        servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
        docs_url: str = "/docs",
        redoc_url: str = "/redoc",
        terms_of_service: Optional[str] = None,
        contact: Optional[Dict[str, Union[str, Any]]] = None,
        license_info: Optional[Dict[str, Union[str, Any]]] = None
    ) -> None:
        """Initialize the Pharmacology REST API"""
        
        # Define OpenAPI tags if not provided
        if openapi_tags is None:
            openapi_tags = [
                {
                    "name": "targets",
                    "description": "Operations related to pharmacological targets (receptors, enzymes, ion channels, etc.)",
                },
                {
                    "name": "ligands",
                    "description": "Operations related to ligands (drugs, endogenous compounds, etc.)",
                },
                {
                    "name": "interactions",
                    "description": "Operations related to target-ligand interactions",
                },
                {
                    "name": "diseases",
                    "description": "Operations related to diseases",
                },
            ]
        
        # Initialize the parent FastAPI class
        super().__init__(
            debug=debug,
            title=title,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=openapi_tags,
            servers=servers,
            docs_url=docs_url,
            redoc_url=redoc_url,
            swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect" if docs_url else None,
            swagger_ui_init_oauth=None,
            middleware=None,
            exception_handlers=None,
            on_startup=None,
            on_shutdown=None,
            terms_of_service=terms_of_service,
            contact=contact,
            license_info=license_info,
        )
        
        # Configure routes from mixins
        self._target_routes_config()
        self._ligand_routes_config()
        self._interaction_routes_config()
        self._disease_routes_config()
        
        # Add root endpoint
        @self.get("/")
        async def root():
            """Root endpoint that redirects to documentation"""
            return RedirectResponse(url="/docs") 