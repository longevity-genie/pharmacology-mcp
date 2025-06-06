from functools import partial
import os
from pathlib import Path
from enum import Enum

import anyio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import typer
from typing_extensions import Annotated

from pharmacology_mcp.pharmacology_api import PharmacologyRestAPI
from pycomfort.logging import to_nice_stdout, to_nice_file
from fastmcp import FastMCP
from .local import pharmacology_local_mcp

class TransportType(str, Enum):
    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"
    SSE = "sse"

# Load environment variables
load_dotenv()

# Configuration
DEFAULT_HOST = os.getenv("MCP_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("MCP_PORT", "8000"))
DEFAULT_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = PharmacologyRestAPI()
        
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

cli_app = typer.Typer(help="Pharmacology MCP Server CLI")

def cli_app_stdio():
    """CLI app with stdio transport as default"""
    import sys
    # If no transport argument is provided, add stdio as default
    if not any(arg.startswith('--transport') for arg in sys.argv[1:]):
        sys.argv.extend(['--transport', 'stdio'])
    cli_app()
    
def cli_app_sse():
    """CLI app that forces SSE transport"""
    import sys
    # Remove any existing transport arguments and force sse
    sys.argv = [arg for arg in sys.argv if not arg.startswith('--transport')]
    sys.argv.extend(['--transport', 'sse'])
    cli_app()

def run_server_stdio():
    """Run the server with stdio transport"""
    transport = "stdio"
    app = create_app()
    mcp = FastMCP.from_fastapi(app=app, port=DEFAULT_PORT)
    mcp.mount("local", pharmacology_local_mcp)
    anyio.run(partial(mcp.run_async, transport=transport))
    
@cli_app.command()
def run_server(
    host: Annotated[str, typer.Option(help="Host to run the server on.")] = DEFAULT_HOST,
    port: Annotated[int, typer.Option(help="Port to run the server on.")] = DEFAULT_PORT,
    transport: Annotated[str, typer.Option(help="Transport type: stdio, streamable-http, or sse")] = DEFAULT_TRANSPORT
):
    """Runs the Pharmacology MCP server."""
    # Validate transport value
    if transport not in ["stdio", "streamable-http", "sse"]:
        typer.echo(f"Invalid transport: {transport}. Must be one of: stdio, streamable-http, sse")
        raise typer.Exit(1)
        
    app = create_app()
    mcp = FastMCP.from_fastapi(app=app, port=DEFAULT_PORT)

    # Manually add routes from the original FastAPI app to FastMCP's additional routes
    if mcp._additional_http_routes is None:
        mcp._additional_http_routes = []
    
    # Add all routes from the original app.
    for route in app.routes:
        mcp._additional_http_routes.append(route)

    # Different transports need different arguments
    if transport == "stdio":
        run_server_stdio()
    else:
        anyio.run(partial(mcp.run_async, transport=transport, host=host, port=port))

if __name__ == "__main__":
    to_nice_stdout()
    # Determine project root and logs directory
    project_root = Path(__file__).resolve().parents[2]
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

    # Define log file paths
    json_log_path = log_dir / "mcp_server.log.json"
    rendered_log_path = log_dir / "mcp_server.log"
    
    # Configure file logging
    to_nice_file(output_file=json_log_path, rendered_file=rendered_log_path)
    cli_app() 