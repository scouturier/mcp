import asyncio
import logging
import os
from awslabs.aws_location_server.server import (
    get_place,
    reverse_geocode,
    search_nearby,
    search_places,
    search_places_open_now,
)
from mcp.server.fastmcp import Context


# Set up a logger instead of using print for sensitive data
logger = logging.getLogger('integration_tests')
logger.setLevel(logging.INFO)
# Only log to console during development, not in production
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class DummyContext(Context):
    """Dummy context for testing."""

    async def error(self, message=None, **extra):
        """Handle error messages for DummyContext."""
        logger.error(message)


def log_place(place):
    """Log details of a place for integration test output."""
    # Avoid logging potentially sensitive information
    # Only log non-sensitive fields
    if place:
        logger.info('Place details:')
        if 'name' in place:
            logger.info(f'Name: {place.get("name")}')
        if 'address' in place:
            # Address could contain PII, so we'll just log that it exists
            logger.info('Address: [Address information available]')
        
        # Log categories as they're generally not sensitive
        if 'categories' in place and place.get('categories'):
            logger.info(f'Categories: {", ".join(place.get("categories", []))}')
        
        # Log that coordinates exist but not their values
        if 'coordinates' in place and place.get('coordinates'):
            logger.info('Coordinates: [Coordinate information available]')
        
        # Log that contact info exists but not the actual values
        if 'contacts' in place and place.get('contacts'):
            logger.info('Contact information: [Available]')
        
        logger.info('-')


async def main():
    """Run integration tests for AWS Location MCP server."""
    # Ensure AWS credentials and region are set
    if not (os.environ.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_PROFILE')):
        logger.error('AWS credentials not set.')
        return
    if not os.environ.get('AWS_REGION'):
        logger.error('AWS_REGION not set.')
        return

    ctx = DummyContext(_request_context=None, _fastmcp=None)

    logger.info('\n=== search_places (POI query) ===')
    search_result = await search_places(ctx, query='Starbucks, Seattle', max_results=3)
    places = search_result.get('places', [])
    if not places:
        logger.info('No places found in search_places.')
        return
    
    logger.info(f'Found {len(places)} places')
    for place in places:
        log_place(place)

    # Use the first place_id and coordinates for further tests
    first_place = places[0]
    place_id = first_place.get('place_id', '')
    # Don't log the actual place_id as it could be considered sensitive
    has_place_id = bool(place_id)
    
    # Store coordinates for testing but don't log them
    longitude = first_place.get('coordinates', {}).get('longitude', None)
    latitude = first_place.get('coordinates', {}).get('latitude', None)
    has_coordinates = longitude is not None and latitude is not None and longitude != 0 and latitude != 0

    logger.info('\n=== get_place ===')
    if has_place_id:
        get_place_result = await get_place(ctx, place_id=place_id)
        if get_place_result.get('name') == 'Unknown' or not get_place_result.get('address'):
            logger.info('No valid data found in get_place.')
        else:
            log_place(get_place_result)
    else:
        logger.info('No valid place_id found for get_place test.')

    logger.info('\n=== reverse_geocode ===')
    if has_coordinates:
        reverse_geocode_result = await reverse_geocode(ctx, longitude=longitude, latitude=latitude)
        logger.info('Reverse geocode result:')
        # Don't log the actual address or coordinates
        if 'address' in reverse_geocode_result:
            logger.info('Address: [Address information available]')
        if 'coordinates' in reverse_geocode_result:
            logger.info('Coordinates: [Coordinate information available]')
    else:
        logger.info('No valid coordinates found for reverse_geocode test.')

    logger.info('\n=== search_nearby (with radius expansion) ===')
    if has_coordinates:
        # Start with a very small radius to force expansion
        search_nearby_result = await search_nearby(
            ctx,
            longitude=longitude,
            latitude=latitude,
            max_results=3,
            radius=10,
            max_radius=2000,
            expansion_factor=2.0,
        )
        nearby_places = search_nearby_result.get('places', [])
        radius_used = search_nearby_result.get('radius_used', None)
        if not nearby_places:
            logger.info(
                f'No places found in search_nearby after expanding radius up to {radius_used}m.'
            )
        else:
            logger.info(f'Found {len(nearby_places)} places with radius {radius_used}m:')
            for place in nearby_places:
                log_place(place)
    else:
        logger.info('No valid coordinates found for search_nearby test.')

    logger.info('\n=== search_places_open_now (with radius expansion) ===')
    query = 'Starbucks, Seattle'
    open_now_result = await search_places_open_now(
        ctx, query=query, max_results=3, initial_radius=10, max_radius=2000, expansion_factor=2.0
    )
    logger.info(f'Query: {query}')
    open_places = open_now_result.get('open_places', [])
    radius_used = open_now_result.get('radius_used', None)
    if not open_places:
        logger.info(f'No places found open now after expanding radius up to {radius_used}m.')
    else:
        logger.info(f'{len(open_places)} places open now (radius used: {radius_used}m):')
        for place in open_places:
            logger.info(f'Name: {place.get("name")}')
            # Don't log the actual address
            logger.info('Address: [Address information available]')
            logger.info(f'Open Now: {place.get("open_now")}')
            
            # Log opening hours without specific details
            if place.get('opening_hours'):
                logger.info(f'Opening Hours: [Available - {len(place.get("opening_hours"))} entries]')
            logger.info('-')

    logger.info('\n=== search_places_open_now (7-Eleven, New York, with radius expansion) ===')
    query_7e = '7-Eleven, New York'
    open_now_result_7e = await search_places_open_now(
        ctx,
        query=query_7e,
        max_results=3,
        initial_radius=10,
        max_radius=2000,
        expansion_factor=2.0,
    )
    logger.info(f'Query: {query_7e}')
    open_places_7e = open_now_result_7e.get('open_places', [])
    radius_used_7e = open_now_result_7e.get('radius_used', None)
    if not open_places_7e:
        logger.info(f'No places found open now after expanding radius up to {radius_used_7e}m.')
    else:
        logger.info(f'{len(open_places_7e)} places open now (radius used: {radius_used_7e}m):')
        for place in open_places_7e:
            logger.info(f'Name: {place.get("name")}')
            # Don't log the actual address
            logger.info('Address: [Address information available]')
            logger.info(f'Open Now: {place.get("open_now")}')
            
            # Log opening hours without specific details
            if place.get('opening_hours'):
                logger.info(f'Opening Hours: [Available - {len(place.get("opening_hours"))} entries]')
            logger.info('-')

    logger.info('\n=== search_places_open_now (mall, Princeton, NJ, with radius expansion) ===')
    query_mall = 'mall, Princeton, NJ'
    open_now_result_mall = await search_places_open_now(
        ctx,
        query=query_mall,
        max_results=3,
        initial_radius=10,
        max_radius=2000,
        expansion_factor=2.0,
    )
    logger.info(f'Query: {query_mall}')
    open_places_mall = open_now_result_mall.get('open_places', [])
    radius_used_mall = open_now_result_mall.get('radius_used', None)
    if not open_places_mall:
        logger.info(f'No malls found open now after expanding radius up to {radius_used_mall}m.')
    else:
        logger.info(f'{len(open_places_mall)} malls open now (radius used: {radius_used_mall}m):')
        for place in open_places_mall:
            logger.info(f'Name: {place.get("name")}')
            # Don't log the actual address
            logger.info('Address: [Address information available]')
            logger.info(f'Open Now: {place.get("open_now")}')
            
            # Log opening hours without specific details
            if place.get('opening_hours'):
                logger.info(f'Opening Hours: [Available - {len(place.get("opening_hours"))} entries]')
            logger.info('-')

    logger.info('\n=== search_places (mall, Princeton, NJ, with operating hours) ===')
    query_mall = 'mall, Princeton, NJ'
    search_result_mall = await search_places(ctx, query=query_mall, max_results=3)
    places_mall = search_result_mall.get('places', [])
    if not places_mall:
        logger.info('No malls found in search_places.')
    else:
        logger.info(f'{len(places_mall)} malls found:')
        for place in places_mall:
            log_place(place)

    # Additional POI test cases
    test_cases = [
        ('hospital, Boston, MA', 5),
        ('school, Palo Alto, CA', 5),
        ('restaurant, Paris, France', 5),
        ('gas station, Houston, TX', 5),
        ('pharmacy, Tokyo, Japan', 5),
        ('cafe, London, UK', 2),  # To confirm optional result count
    ]
    for query, max_results in test_cases:
        logger.info(f'\n=== search_places ({query}, max_results={max_results}) ===')
        search_result = await search_places(
            ctx, query=query, max_results=max_results, mode='summary'
        )
        places = search_result.get('places', [])
        if not places:
            logger.info(f"No places found for query '{query}'.")
        else:
            logger.info(f'{len(places)} places found:')
            for place in places:
                log_place(place)

    logger.info('Integration tests completed successfully.')


if __name__ == '__main__':
    asyncio.run(main())
