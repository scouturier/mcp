# AWS Location Service MCP Server

A Model Context Protocol (MCP) server that provides access to AWS Location Service capabilities, focusing on place search and geographical coordinates.

## Features

- Search for places using geocoding
- Get coordinates for locations

## Prerequisites

Before using this MCP server, you need to:

1. Have an AWS account with AWS Location Service enabled
2. Create a Place Index in AWS Location Service (or the server will attempt to use an existing one)
3. Configure AWS CLI with your credentials and profile

## Installation

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

## Configuration

Configure the server in your MCP settings:

```json
{
  "mcpServers": {
    "awslabs.aws-location-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-location-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "us-east-1",
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_LOCATION_PLACE_INDEX": "your-place-index-name"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

> **Important Note**: Make sure to use `awslabs.aws-location-mcp-server@latest` in the args array, not `awslabs.aws_location_server@latest`. The package name must match the repository name with hyphens (-), not underscores (_).

### Environment Variables

- `AWS_PROFILE`: AWS CLI profile to use for credentials
- `AWS_REGION`: AWS region to use (default: us-east-1)
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: Explicit AWS credentials (alternative to AWS_PROFILE)
- `AWS_LOCATION_PLACE_INDEX`: Name of the AWS Location Service Place Index to use (default: ExamplePlaceIndex)

## Tools

### search_places

Search for places using AWS Location Service geocoding.

**Parameters:**
- `query` (required): Search query (address, place name, etc.)
- `max_results` (optional): Maximum number of results to return (1-50, default: 5)

**Example:**
```json
{
  "query": "Empire State Building",
  "max_results": 3
}
```

### get_coordinates

Get coordinates for a specific location.

**Parameters:**
- `location` (required): Location name (city, address, landmark, etc.)

**Example:**
```json
{
  "location": "Quebec City, Canada"
}
```

**Response includes:**
- Location name
- Formatted address
- Coordinates (longitude, latitude)
- Country, region, and municipality information

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

This server uses the following AWS Location Service resource:

**Place Index**: Used for geocoding and place search
- Create in AWS Console: Amazon Location Service > Place indexes > Create place index
- Recommended data provider: Esri or HERE
- If not specified, the server will attempt to use an existing place index

## Security Considerations

- Use AWS profiles for credential management
- Use IAM policies to restrict access to only the required AWS Location Service resources
- Consider using temporary credentials or AWS IAM roles for enhanced security
