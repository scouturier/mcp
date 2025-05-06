# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.
"""Tests for AWS Location Service MCP Server."""

import pytest
from awslabs.aws_location_server.server import search_places
from unittest.mock import patch


@pytest.mark.asyncio
async def test_search_places(mock_boto3_client, mock_context):
    """Test the search_places tool."""
    # Set up test data
    query = 'Seattle'
    max_results = 5

    # Patch the geo_places_client in the server module
    with patch('awslabs.aws_location_server.server.geo_places_client') as mock_geo_client:
        mock_geo_client.geo_places_client = mock_boto3_client
        result = await search_places(mock_context, query=query, max_results=max_results)

    # Verify the result (update as needed based on new API)
    assert result['query'] == query
    # The rest of the assertions may need to be updated based on the new output structure


def test_geo_places_client_initialization(monkeypatch):
    """Test the GeoPlacesClient initialization."""
    # NOTE: No AWS credentials are set or required for this test. All AWS calls are mocked.
    monkeypatch.setenv('AWS_REGION', 'us-west-2')
    with patch('boto3.client') as mock_boto3_client:
        from awslabs.aws_location_server.server import GeoPlacesClient

        GeoPlacesClient()
        mock_boto3_client.assert_called_once()
        args, kwargs = mock_boto3_client.call_args
        assert args[0] == 'geo-places'
        assert kwargs['region_name'] == 'us-west-2'
