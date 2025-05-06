# AWS Location Service MCP Server

Model Context Protocol (MCP) server for AWS Location Service

This MCP server provides tools to access AWS Location Service capabilities, focusing on place search and geographical coordinates.

## Features

- **Search for Places**: Search for places using geocoding
- **Get Place Details**: Get details for specific places by PlaceId
- **Reverse Geocode**: Convert coordinates to addresses
- **Search Nearby**: Search for places near a specified location
- **Open Now Search**: Search for places that are currently open

## Prerequisites

### Requirements

1. Have an AWS account with AWS Location Service enabled
2. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
3. Install Python 3.10 or newer using `uv python install 3.10` (or a more recent version)

## Installation

Here are the ways you can work with the AWS Location MCP server:

## Configuration

Configure the server in your MCP configuration file. Here are some ways you can work with MCP across AWS, and we'll be adding support to more products soon: (e.g. for Amazon Q Developer CLI MCP, `~/.aws/amazonq/mcp.json`):

```json
{
  "mcpServers": {
    "awslabs.aws-location-mcp-server": {
        "command": "uvx",
        "args": ["awslabs.aws-location-mcp-server@latest"],
        "env": {
          "AWS_PROFILE": "your-aws-profile",
          "AWS_REGION": "us-east-1",
          "FASTMCP_LOG_LEVEL": "ERROR"
        },
        "disabled": false,
        "autoApprove": []
    }
  }
}
```

### Docker Configuration

After building with `docker build -t awslabs/aws-location-mcp-server .`:

```json
{
  "mcpServers": {
    "awslabs.aws-location-mcp-server": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "-i",
          "awslabs/aws-location-mcp-server"
        ],
        "env": {
          "AWS_PROFILE": "your-aws-profile",
          "AWS_REGION": "us-east-1"
        },
        "disabled": false,
        "autoApprove": []
    }
  }
}
```

### Environment Variables

- `AWS_PROFILE`: AWS CLI profile to use for credentials
- `AWS_REGION`: AWS region to use (default: us-east-1)
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: Explicit AWS credentials (alternative to AWS_PROFILE)
- `FASTMCP_LOG_LEVEL`: Logging level (ERROR, WARNING, INFO, DEBUG)

## Tools

The server exposes the following tools through the MCP interface:

### search_places

Search for places using AWS Location Service geocoding capabilities.

```python
search_places(query: str, max_results: int = 5, mode: str = 'summary') -> dict
```

### get_place

Get details for a specific place using its unique place ID.

```python
get_place(place_id: str, mode: str = 'summary') -> dict
```

### reverse_geocode

Convert coordinates to an address using reverse geocoding.

```python
reverse_geocode(longitude: float, latitude: float) -> dict
```

### search_nearby

Search for places near a specific location with optional radius expansion.

```python
search_nearby(longitude: float, latitude: float, radius: int = 500, max_results: int = 5, 
              query: str = None, max_radius: int = 10000, expansion_factor: float = 2.0, 
              mode: str = 'summary') -> dict
```

### search_places_open_now

Search for places that are currently open, with radius expansion if needed.

```python
search_places_open_now(query: str, max_results: int = 5, initial_radius: int = 500, 
                       max_radius: int = 50000, expansion_factor: float = 2.0) -> dict
```

### get_coordinates

Get coordinates for a location name or address.

```python
get_coordinates(location: str) -> dict
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
