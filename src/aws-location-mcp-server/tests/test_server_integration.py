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
logger = logging.getLogger("integration_tests")
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
    logger.info(f'Name: {place.get("name")}')
    logger.info(f'Address: {place.get("address")}')
    contacts = place.get('contacts', {})
    if contacts:
        if contacts.get('phones'):
            logger.info(f'Phones: {", ".join(contacts["phones"])}')
        if contacts.get('websites'):
            logger.info(f'Websites: {", ".join(contacts["websites"])}')
        # Don't log emails as they could be PII
        if contacts.get('faxes'):
            logger.info(f'Faxes: {", ".join(contacts["faxes"])}')
    logger.info(f'Categories: {", ".join(place.get("categories", []))}')
    coords = place.get('coordinates', {})
    logger.info(f'Coordinates: {coords.get("longitude")}, {coords.get("latitude")}')
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
        # Don't log raw results as they might contain sensitive information
        return
    for place in places:
        log_place(place)

    # Use the first place_id and coordinates for further tests
    first_place = places[0]
    place_id = first_place.get('place_id', '')
    longitude = first_place.get('coordinates', {}).get('longitude', None)
    latitude = first_place.get('coordinates', {}).get('latitude', None)

    logger.info('\n=== get_place ===')
    if place_id:
        get_place_result = await get_place(ctx, place_id=place_id)
        if get_place_result.get('name') == 'Unknown' or not get_place_result.get('address'):
            logger.info('No valid data found in get_place.')
        else:
            log_place(get_place_result)
    else:
        logger.info('No valid place_id found for get_place test.')

    logger.info('\n=== reverse_geocode ===')
    if longitude is not None and latitude is not None and longitude != 0 and latitude != 0:
        reverse_geocode_result = await reverse_geocode(ctx, longitude=longitude, latitude=latitude)
        # Log only address and coordinates
        address = reverse_geocode_result.get('address', '')
        coords = reverse_geocode_result.get('coordinates', {})
        logger.info(f'Address: {address}')
        logger.info(f'Coordinates: {coords.get("longitude")}, {coords.get("latitude")}')
    else:
        logger.info('No valid coordinates found for reverse_geocode test.')

    logger.info('\n=== search_nearby (with radius expansion) ===')
    if longitude is not None and latitude is not None and longitude != 0 and latitude != 0:
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
            logger.info(f'Address: {place.get("address")}')
            logger.info(f'Open Now: {place.get("open_now")}')
            logger.info('Opening Hours:')
            for oh in place.get('opening_hours', []):
                display = oh.get('display', [])
                open_now = oh.get('open_now', False)
                categories = oh.get('categories', [])
                logger.info(
                    f'  - {"; ".join(display)} | Open Now: {open_now} | Categories: {", ".join(categories)}'
                )
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
            logger.info(f'Address: {place.get("address")}')
            logger.info(f'Open Now: {place.get("open_now")}')
            logger.info('Opening Hours:')
            for oh in place.get('opening_hours', []):
                display = oh.get('display', [])
                open_now = oh.get('open_now', False)
                categories = oh.get('categories', [])
                logger.info(
                    f'  - {"; ".join(display)} | Open Now: {open_now} | Categories: {", ".join(categories)}'
                )
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
            logger.info(f'Address: {place.get("address")}')
            logger.info(f'Open Now: {place.get("open_now")}')
            logger.info('Operating Hours:')
            for oh in place.get('opening_hours', []):
                display = oh.get('display', [])
                open_now = oh.get('open_now', False)
                categories = oh.get('categories', [])
                logger.info(
                    f'  - {"; ".join(display)} | Open Now: {open_now} | Categories: {", ".join(categories)}'
                )
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
            logger.info(f'Name: {place.get("name", "Not available")}')
            logger.info(f'Address: {place.get("address", "Not available")}')
            contacts = place.get('contacts', {})
            logger.info(f'Phones: {", ".join(contacts.get("phones", [])) or "Not available"}')
            logger.info(f'Websites: {", ".join(contacts.get("websites", [])) or "Not available"}')
            # Don't log emails as they could be PII
            logger.info(f'Faxes: {", ".join(contacts.get("faxes", [])) or "Not available"}')
            logger.info(f'Categories: {", ".join(place.get("categories", [])) or "Not available"}')
            coords = place.get('coordinates', {})
            logger.info(
                f'Coordinates: {coords.get("longitude", "Not available")}, {coords.get("latitude", "Not available")}'
            )
            opening_hours = place.get('opening_hours', [])
            if opening_hours:
                logger.info('Operating Hours:')
                for oh in opening_hours:
                    display = oh.get('display', [])
                    components = oh.get('components', [])
                    open_now = oh.get('open_now', None)
                    categories = oh.get('categories', [])
                    logger.info(f'  - Display: {"; ".join(display) if display else "Not available"}')
                    logger.info(f'    Components: {components if components else "Not available"}')
                    logger.info(f'    Open Now: {open_now if open_now is not None else "Not available"}')
                    logger.info(
                        f'    Categories: {", ".join(categories) if categories else "Not available"}'
                    )
            else:
                logger.info('Operating Hours: Not available')
            logger.info('-')

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
                logger.info(f'Name: {place.get("name", "Not available")}')
                logger.info(f'Address: {place.get("address", "Not available")}')
                contacts = place.get('contacts', {})
                logger.info(f'Phones: {", ".join(contacts.get("phones", [])) or "Not available"}')
                logger.info(f'Websites: {", ".join(contacts.get("websites", [])) or "Not available"}')
                # Don't log emails as they could be PII
                logger.info(f'Faxes: {", ".join(contacts.get("faxes", [])) or "Not available"}')
                logger.info(f'Categories: {", ".join(place.get("categories", [])) or "Not available"}')
                coords = place.get('coordinates', {})
                logger.info(
                    f'Coordinates: {coords.get("longitude", "Not available")}, {coords.get("latitude", "Not available")}'
                )
                opening_hours = place.get('opening_hours', [])
                if opening_hours:
                    logger.info('Operating Hours:')
                    for oh in opening_hours:
                        display = oh.get('display', [])
                        components = oh.get('components', [])
                        open_now = oh.get('open_now', None)
                        categories = oh.get('categories', [])
                        logger.info(f'  - Display: {"; ".join(display) if display else "Not available"}')
                        logger.info(f'    Components: {components if components else "Not available"}')
                        logger.info(
                            f'    Open Now: {open_now if open_now is not None else "Not available"}'
                        )
                        logger.info(
                            f'    Categories: {", ".join(categories) if categories else "Not available"}'
                        )
                else:
                    logger.info('Operating Hours: Not available')
                logger.info('-')

    logger.info('Integration tests completed successfully.')


if __name__ == '__main__':
    asyncio.run(main())
