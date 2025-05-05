# AWS Location Service MCP Server

A Model Context Protocol (MCP) server that provides access to AWS Location Service capabilities, focusing on place search and geographical coordinates.

## Features

- Search for places using geocoding
- Get details for specific places by PlaceId
- Reverse geocode coordinates to addresses
- Search for places near a location
- Search for places that are currently open

## Prerequisites

Before using this MCP server, you need to:

1. Have an AWS account with AWS Location Service enabled
2. Configure AWS CLI with your credentials and profile

## Installation

There are two ways to install and configure the AWS Location MCP server:

### Option 1: Using uvx (Recommended)

This is the standard way to install MCP servers and is consistent with other AWS MCP servers:

```bash
# Install the package using uvx
uvx awslabs.aws-location-mcp-server@latest
```

### Option 2: Local Development Installation

If you're developing or modifying the server, or if Option 1 doesn't work:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/awslabs/mcp.git
cd mcp/src/aws-location-mcp-server

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

## Configuration

Configure the server in your MCP settings:

### Option 1: Standard Configuration (Recommended)

```json
{
  "mcpServers": {
    "github.com/awslabs/mcp/tree/main/src/aws-location-mcp-server": {
      "autoApprove": [
        "search_places",
        "get_place",
        "reverse_geocode",
        "search_nearby",
        "search_places_open_now"
      ],
      "disabled": false,
      "timeout": 60,
      "command": "uvx",
      "args": [
        "awslabs.aws-location-mcp-server@latest"
      ],
      "env": {
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "us-east-1",
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "transportType": "stdio"
    }
  }
}
```

### Option 2: Local Development Configuration - Direct Python Executable (Recommended for local development)

This approach directly uses the Python executable from the virtual environment:

```json
{
  "mcpServers": {
    "github.com/awslabs/mcp/tree/main/src/aws-location-mcp-server": {
      "autoApprove": [
        "search_places",
        "get_place",
        "reverse_geocode",
        "search_nearby",
        "search_places_open_now"
      ],
      "disabled": false,
      "timeout": 60,
      "command": "/path/to/mcp/src/aws-location-mcp-server/.venv/bin/python",
      "args": [
        "-m",
        "awslabs.aws_location_server.server"
      ],
      "env": {
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "us-east-1",
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "transportType": "stdio"
    }
  }
}
```

### Option 3: Local Development Configuration - Using bash

An alternative approach using bash to activate the virtual environment:

```json
{
  "mcpServers": {
    "github.com/awslabs/mcp/tree/main/src/aws-location-mcp-server": {
      "autoApprove": [
        "search_places",
        "get_place",
        "reverse_geocode",
        "search_nearby",
        "search_places_open_now"
      ],
      "disabled": false,
      "timeout": 60,
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/mcp/src/aws-location-mcp-server && source .venv/bin/activate && python -m awslabs.aws_location_server.server"
      ],
      "env": {
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "us-east-1",
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "transportType": "stdio"
    }
  }
}
```

> **Important Note**: Make sure to use `awslabs.aws-location-mcp-server@latest` in the args array, not `awslabs.aws_location_server@latest`. The package name must match the repository name with hyphens (-), not underscores (_).

### Environment Variables

- `AWS_PROFILE`: AWS CLI profile to use for credentials
- `AWS_REGION`: AWS region to use (default: us-east-1)
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: Explicit AWS credentials (alternative to AWS_PROFILE)

## Tools

### search_places

Search for places using AWS Location Service geo-places search_text API.

**Parameters:**
- `query` (required): Search query (address, place name, etc.)
- `max_results` (optional): Maximum number of results to return (1-50, default: 5)
- `mode` (optional): Output mode: 'summary' (default) or 'raw' for all AWS fields

**Example:**
```json
{
  "query": "Empire State Building",
  "max_results": 3
}
```

### get_place

Get details for a place using AWS Location Service geo-places get_place API.

**Parameters:**
- `place_id` (required): The unique PlaceId for the place
- `mode` (optional): Output mode: 'summary' (default) or 'raw' for all AWS fields

**Example:**
```json
{
  "place_id": "AQAAAIAADsn1T3KdrRWeaXLeVEyjNx_JfeTsMB0TKUYrAJkOQH-9Cb-I",
  "mode": "summary"
}
```

### reverse_geocode

Reverse geocode coordinates to an address using AWS Location Service geo-places reverse_geocode API.

**Parameters:**
- `longitude` (required): Longitude of the location
- `latitude` (required): Latitude of the location

**Example:**
```json
{
  "longitude": -73.9857,
  "latitude": 40.7484
}
```

### search_nearby

Search for places near a location using AWS Location Service geo-places search_nearby API.

**Parameters:**
- `longitude` (required): Longitude of the center point
- `latitude` (required): Latitude of the center point
- `max_results` (optional): Maximum number of results to return (1-50, default: 5)
- `query` (optional): Optional search query
- `radius` (optional): Search radius in meters (default: 500)
- `max_radius` (optional): Maximum search radius in meters for expansion (default: 10000)
- `expansion_factor` (optional): Factor to expand radius by if no results (default: 2.0)
- `mode` (optional): Output mode: 'summary' (default) or 'raw' for all AWS fields

**Example:**
```json
{
  "longitude": -73.9857,
  "latitude": 40.7484,
  "radius": 1000,
  "max_results": 10
}
```

### search_places_open_now

Search for places that are open now using AWS Location Service geo-places search_text API and filter by opening hours.

**Parameters:**
- `query` (required): Search query (address, place name, etc.)
- `max_results` (optional): Maximum number of results to return (1-50, default: 5)
- `initial_radius` (optional): Initial search radius in meters for expansion (default: 500)
- `max_radius` (optional): Maximum search radius in meters for expansion (default: 50000)
- `expansion_factor` (optional): Factor to expand radius by if no open places (default: 2.0)

**Example:**
```json
{
  "query": "restaurants, New York",
  "max_results": 5
}
```

## Output Structure

All tools that return places (e.g., search_places, search_nearby, get_place) return a standardized structure for each place:

```
{
  "place_id": string, // Unique identifier for the place (or 'Not available')
  "name": string,     // Name of the place (or 'Not available')
  "address": string,  // Full address (or 'Not available')
  "contacts": {
    "phones": [string],    // List of phone numbers (may be empty)
    "websites": [string],  // List of website URLs (may be empty)
    "emails": [string],    // List of email addresses (may be empty)
    "faxes": [string]      // List of fax numbers (may be empty)
  },
  "categories": [string], // List of categories (may be empty)
  "coordinates": {
    "longitude": float or 'Not available',
    "latitude": float or 'Not available'
  },
  "opening_hours": [      // List of opening hours entries (may be empty)
    {
      "display": [string],    // Human-readable display strings (e.g., 'Mon-Fri: 08:00 - 17:00')
      "components": [object], // Raw AWS components for each period (may be empty)
      "open_now": bool or null, // True/False if currently open, or null if unknown
      "categories": [string]  // Categories for this period (may be empty)
    }
  ]
}
```

- All fields are always present. If data is missing, the field is an empty list or 'Not available'.
- The `mode` parameter can be set to 'summary' (default, standardized output) or 'raw' (full AWS response for each place).
- The `max_results` parameter controls the number of results returned (default 5, can be set per request).

## Example Usage

```
# Search for hospitals in Boston, MA, return up to 5 results
await search_places(ctx, query="hospital, Boston, MA", max_results=5)

# Get full AWS response for a place
await get_place(ctx, place_id="...", mode="raw")

# Reverse geocode coordinates
await reverse_geocode(ctx, longitude=-73.9857, latitude=40.7484)

# Search for places near a location
await search_nearby(ctx, longitude=-73.9857, latitude=40.7484, radius=1000)

# Search for restaurants that are open now
await search_places_open_now(ctx, query="restaurants, New York")
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/awslabs/mcp.git
cd mcp/src/aws-location-mcp-server

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run tests with coverage
./run_tests.sh

# Or manually
python -m pytest tests/ -v --cov=awslabs --cov-report=term-missing
```

## AWS Location Service Resources

This server uses the AWS Location Service geo-places API for:
- Geocoding (converting addresses to coordinates)
- Reverse geocoding (converting coordinates to addresses)
- Place search (finding places by name, category, etc.)
- Place details (getting information about specific places)

## Security Considerations

- Use AWS profiles for credential management
- Use IAM policies to restrict access to only the required AWS Location Service resources
- Consider using temporary credentials or AWS IAM roles for enhanced security
