import os
import asyncio
from awslabs.aws_location_server.server import search_places, get_place, reverse_geocode, search_nearby, search_places_open_now
from mcp.server.fastmcp import Context

class DummyContext(Context):
    async def error(self, msg):
        print(f"[ERROR] {msg}")

def print_place(place):
    print(f"Name: {place.get('name')}")
    print(f"Address: {place.get('address')}")
    contacts = place.get('contacts', {})
    if contacts:
        if contacts.get('phones'):
            print(f"Phones: {', '.join(contacts['phones'])}")
        if contacts.get('websites'):
            print(f"Websites: {', '.join(contacts['websites'])}")
        if contacts.get('emails'):
            print(f"Emails: {', '.join(contacts['emails'])}")
        if contacts.get('faxes'):
            print(f"Faxes: {', '.join(contacts['faxes'])}")
    print(f"Categories: {', '.join(place.get('categories', []))}")
    coords = place.get('coordinates', {})
    print(f"Coordinates: {coords.get('longitude')}, {coords.get('latitude')}")
    print("-")

async def main():
    # Ensure AWS credentials and region are set
    if not (os.environ.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_PROFILE')):
        print("AWS credentials not set.")
        return
    if not os.environ.get('AWS_REGION'):
        print("AWS_REGION not set.")
        return

    ctx = DummyContext()

    print("\n=== search_places (POI query) ===")
    search_result = await search_places(ctx, query="Starbucks, Seattle", max_results=3)
    places = search_result.get('places', [])
    if not places:
        print("No places found in search_places. Raw result:")
        print(search_result)
        return
    for place in places:
        print_place(place)

    # Use the first place_id and coordinates for further tests
    first_place = places[0]
    place_id = first_place.get('place_id', '')
    longitude = first_place.get('coordinates', {}).get('longitude', None)
    latitude = first_place.get('coordinates', {}).get('latitude', None)

    print("\n=== get_place ===")
    if place_id:
        get_place_result = await get_place(ctx, place_id=place_id)
        if get_place_result.get('name') == 'Unknown' or not get_place_result.get('address'):
            print("No valid data found in get_place. Raw result:")
            print(get_place_result)
        else:
            print_place(get_place_result)
    else:
        print("No valid place_id found for get_place test.")

    print("\n=== reverse_geocode ===")
    if longitude is not None and latitude is not None and longitude != 0 and latitude != 0:
        reverse_geocode_result = await reverse_geocode(ctx, longitude=longitude, latitude=latitude)
        # Print only address and coordinates
        address = reverse_geocode_result.get('address', '')
        coords = reverse_geocode_result.get('coordinates', {})
        print(f"Address: {address}")
        print(f"Coordinates: {coords.get('longitude')}, {coords.get('latitude')}")
    else:
        print("No valid coordinates found for reverse_geocode test.")

    print("\n=== search_nearby (with radius expansion) ===")
    if longitude is not None and latitude is not None and longitude != 0 and latitude != 0:
        # Start with a very small radius to force expansion
        search_nearby_result = await search_nearby(ctx, longitude=longitude, latitude=latitude, max_results=3, radius=10, max_radius=2000, expansion_factor=2.0)
        nearby_places = search_nearby_result.get('places', [])
        radius_used = search_nearby_result.get('radius_used', None)
        if not nearby_places:
            print(f"No places found in search_nearby after expanding radius up to {radius_used}m. Raw result:")
            print(search_nearby_result)
        else:
            print(f"Found {len(nearby_places)} places with radius {radius_used}m:")
            for place in nearby_places:
                print_place(place)
    else:
        print("No valid coordinates found for search_nearby test.")

    print("\n=== search_places_open_now (with radius expansion) ===")
    query = "Starbucks, Seattle"
    open_now_result = await search_places_open_now(ctx, query=query, max_results=3, initial_radius=10, max_radius=2000, expansion_factor=2.0)
    print(f"Query: {query}")
    open_places = open_now_result.get('open_places', [])
    radius_used = open_now_result.get('radius_used', None)
    if not open_places:
        print(f"No places found open now after expanding radius up to {radius_used}m.")
    else:
        print(f"{len(open_places)} places open now (radius used: {radius_used}m):")
        for place in open_places:
            print(f"Name: {place.get('name')}")
            print(f"Address: {place.get('address')}")
            print(f"Open Now: {place.get('open_now')}")
            print("Opening Hours:")
            for oh in place.get('opening_hours', []):
                display = oh.get('display', [])
                open_now = oh.get('open_now', False)
                categories = oh.get('categories', [])
                print(f"  - {'; '.join(display)} | Open Now: {open_now} | Categories: {', '.join(categories)}")
            print("-")

    print("\n=== search_places_open_now (7-Eleven, New York, with radius expansion) ===")
    query_7e = "7-Eleven, New York"
    open_now_result_7e = await search_places_open_now(ctx, query=query_7e, max_results=3, initial_radius=10, max_radius=2000, expansion_factor=2.0)
    print(f"Query: {query_7e}")
    open_places_7e = open_now_result_7e.get('open_places', [])
    radius_used_7e = open_now_result_7e.get('radius_used', None)
    if not open_places_7e:
        print(f"No places found open now after expanding radius up to {radius_used_7e}m.")
    else:
        print(f"{len(open_places_7e)} places open now (radius used: {radius_used_7e}m):")
        for place in open_places_7e:
            print(f"Name: {place.get('name')}")
            print(f"Address: {place.get('address')}")
            print(f"Open Now: {place.get('open_now')}")
            print("Opening Hours:")
            for oh in place.get('opening_hours', []):
                display = oh.get('display', [])
                open_now = oh.get('open_now', False)
                categories = oh.get('categories', [])
                print(f"  - {'; '.join(display)} | Open Now: {open_now} | Categories: {', '.join(categories)}")
            print("-")

    print("\n=== search_places_open_now (mall, Princeton, NJ, with radius expansion) ===")
    query_mall = "mall, Princeton, NJ"
    open_now_result_mall = await search_places_open_now(ctx, query=query_mall, max_results=3, initial_radius=10, max_radius=2000, expansion_factor=2.0)
    print(f"Query: {query_mall}")
    open_places_mall = open_now_result_mall.get('open_places', [])
    radius_used_mall = open_now_result_mall.get('radius_used', None)
    if not open_places_mall:
        print(f"No malls found open now after expanding radius up to {radius_used_mall}m.")
    else:
        print(f"{len(open_places_mall)} malls open now (radius used: {radius_used_mall}m):")
        for place in open_places_mall:
            print(f"Name: {place.get('name')}")
            print(f"Address: {place.get('address')}")
            print(f"Open Now: {place.get('open_now')}")
            print("Operating Hours:")
            for oh in place.get('opening_hours', []):
                display = oh.get('display', [])
                open_now = oh.get('open_now', False)
                categories = oh.get('categories', [])
                print(f"  - {'; '.join(display)} | Open Now: {open_now} | Categories: {', '.join(categories)}")
            print("-")

    print("\n=== search_places (mall, Princeton, NJ, with operating hours) ===")
    query_mall = "mall, Princeton, NJ"
    search_result_mall = await search_places(ctx, query=query_mall, max_results=3)
    places_mall = search_result_mall.get('places', [])
    if not places_mall:
        print("No malls found in search_places. Raw result:")
        print(search_result_mall)
    else:
        print(f"{len(places_mall)} malls found:")
        for place in places_mall:
            print(f"Name: {place.get('name', 'Not available')}")
            print(f"Address: {place.get('address', 'Not available')}")
            contacts = place.get('contacts', {})
            print(f"Phones: {', '.join(contacts.get('phones', [])) or 'Not available'}")
            print(f"Websites: {', '.join(contacts.get('websites', [])) or 'Not available'}")
            print(f"Emails: {', '.join(contacts.get('emails', [])) or 'Not available'}")
            print(f"Faxes: {', '.join(contacts.get('faxes', [])) or 'Not available'}")
            print(f"Categories: {', '.join(place.get('categories', [])) or 'Not available'}")
            coords = place.get('coordinates', {})
            print(f"Coordinates: {coords.get('longitude', 'Not available')}, {coords.get('latitude', 'Not available')}")
            opening_hours = place.get('opening_hours', [])
            if opening_hours:
                print("Operating Hours:")
                for oh in opening_hours:
                    display = oh.get('display', [])
                    components = oh.get('components', [])
                    open_now = oh.get('open_now', None)
                    categories = oh.get('categories', [])
                    print(f"  - Display: {'; '.join(display) if display else 'Not available'}")
                    print(f"    Components: {components if components else 'Not available'}")
                    print(f"    Open Now: {open_now if open_now is not None else 'Not available'}")
                    print(f"    Categories: {', '.join(categories) if categories else 'Not available'}")
            else:
                print("Operating Hours: Not available")
            print("-")

    # Additional POI test cases
    test_cases = [
        ("hospital, Boston, MA", 5),
        ("school, Palo Alto, CA", 5),
        ("restaurant, Paris, France", 5),
        ("gas station, Houston, TX", 5),
        ("pharmacy, Tokyo, Japan", 5),
        ("cafe, London, UK", 2),  # To confirm optional result count
    ]
    for query, max_results in test_cases:
        print(f"\n=== search_places ({query}, max_results={max_results}) ===")
        search_result = await search_places(ctx, query=query, max_results=max_results, mode='summary')
        places = search_result.get('places', [])
        if not places:
            print(f"No places found for query '{query}'. Raw result:")
            print(search_result)
        else:
            print(f"{len(places)} places found:")
            for place in places:
                print(f"Name: {place.get('name', 'Not available')}")
                print(f"Address: {place.get('address', 'Not available')}")
                contacts = place.get('contacts', {})
                print(f"Phones: {', '.join(contacts.get('phones', [])) or 'Not available'}")
                print(f"Websites: {', '.join(contacts.get('websites', [])) or 'Not available'}")
                print(f"Emails: {', '.join(contacts.get('emails', [])) or 'Not available'}")
                print(f"Faxes: {', '.join(contacts.get('faxes', [])) or 'Not available'}")
                print(f"Categories: {', '.join(place.get('categories', [])) or 'Not available'}")
                coords = place.get('coordinates', {})
                print(f"Coordinates: {coords.get('longitude', 'Not available')}, {coords.get('latitude', 'Not available')}")
                opening_hours = place.get('opening_hours', [])
                if opening_hours:
                    print("Operating Hours:")
                    for oh in opening_hours:
                        display = oh.get('display', [])
                        components = oh.get('components', [])
                        open_now = oh.get('open_now', None)
                        categories = oh.get('categories', [])
                        print(f"  - Display: {'; '.join(display) if display else 'Not available'}")
                        print(f"    Components: {components if components else 'Not available'}")
                        print(f"    Open Now: {open_now if open_now is not None else 'Not available'}")
                        print(f"    Categories: {', '.join(categories) if categories else 'Not available'}")
                else:
                    print("Operating Hours: Not available")
                print("-")

    print("Integration tests completed successfully.")

if __name__ == "__main__":
    asyncio.run(main()) 