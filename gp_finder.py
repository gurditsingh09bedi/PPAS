import googlemaps
import logging
from urllib.parse import urlencode

GOOGLE_MAPS_API_KEY = "****************"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


logging.basicConfig(level=logging.DEBUG)

def find_gp_by_postcode(postcode):
    try:
        
        geocode_result = gmaps.geocode(postcode) # Geocode the postcode to get latitude and longitude
        logging.debug(f"Geocode result for postcode {postcode}: {geocode_result}")

        if not geocode_result:
            logging.error("No geocode result found.")
            return []

        location = geocode_result[0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']

        # Search for GP practices nearby using the Places API
        places_result = gmaps.places_nearby(
            location=(latitude, longitude),
            radius=5000,  # Radius in meters
            type='doctor'  
        )
        logging.debug(f"Places result for location ({latitude, longitude}): {places_result}")

        gps = []
        for place in places_result.get('results', []):
            name = place.get('name', 'N/A')
            address = place.get('vicinity', 'N/A')
            place_location = place['geometry']['location']
            place_latitude = place_location['lat']
            place_longitude = place_location['lng']

            query = f"{place_latitude},{place_longitude}"
            google_maps_url = f"https://www.google.com/maps/search/?{urlencode({'api': '1', 'query': query})}"

            gps.append({
                "Name": name,
                "Address": address,
                "Place ID": place.get('place_id', 'N/A'),
                "Latitude": place_latitude,
                "Longitude": place_longitude,
                "Google Maps URL": google_maps_url
            })

        return gps

    except googlemaps.exceptions.ApiError as e:
        logging.error(f"Google Maps API error: {e}")
        return []
    except googlemaps.exceptions.TransportError as e:
        logging.error(f"Transport error: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return []





