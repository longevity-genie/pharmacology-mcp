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

def setup_logging():
    """Setup logging configuration"""
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

def run_mcp_server(transport: str, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    """Run the MCP server with specified transport"""
    setup_logging()
    
    app = create_app()
    mcp = FastMCP.from_fastapi(app=app, port=port)
    mcp.mount("local", pharmacology_local_mcp)

    # Manually add routes from the original FastAPI app to FastMCP's additional routes
    if mcp._additional_http_routes is None:
        mcp._additional_http_routes = []
    
    # Add all routes from the original app.
    for route in app.routes:
        mcp._additional_http_routes.append(route)

    # Different transports need different arguments
    if transport == "stdio":
        anyio.run(partial(mcp.run_async, transport=transport))
    else:
        anyio.run(partial(mcp.run_async, transport=transport, host=host, port=port))

# Create the main CLI app
cli_app = typer.Typer(help="Pharmacology MCP Server CLI")

@cli_app.command("server")
def server_command(
    host: Annotated[str, typer.Option(help="Host to run the server on.")] = DEFAULT_HOST,
    port: Annotated[int, typer.Option(help="Port to run the server on.")] = DEFAULT_PORT,
    transport: Annotated[str, typer.Option(help="Transport type: stdio, streamable-http, or sse")] = DEFAULT_TRANSPORT
):
    """Run the Pharmacology MCP server with configurable transport."""
    # Validate transport value
    if transport not in ["stdio", "streamable-http", "sse"]:
        typer.echo(f"Invalid transport: {transport}. Must be one of: stdio, streamable-http, sse")
        raise typer.Exit(1)
    
    run_mcp_server(transport=transport, host=host, port=port)

@cli_app.command("stdio")
def stdio_command():
    """Run the Pharmacology MCP server with stdio transport."""
    run_mcp_server(transport="stdio")

@cli_app.command("sse")
def sse_command(
    host: Annotated[str, typer.Option(help="Host to run the server on.")] = DEFAULT_HOST,
    port: Annotated[int, typer.Option(help="Port to run the server on.")] = DEFAULT_PORT,
):
    """Run the Pharmacology MCP server with SSE transport."""
    run_mcp_server(transport="sse", host=host, port=port)

# Entry point functions for pyproject.toml
def cli_app_stdio():
    """Entry point for stdio transport (used by pyproject.toml)"""
    setup_logging()
    run_mcp_server(transport="stdio")

def cli_app_sse():
    """Entry point for SSE transport (used by pyproject.toml)"""
    setup_logging()
    run_mcp_server(transport="sse")

if __name__ == "__main__":
    cli_app() 