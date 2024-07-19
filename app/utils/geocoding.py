import googlemaps
import configparser

# Read API key from config file
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['google_maps']['GOOGLE_API_KEY']
gmaps = googlemaps.Client(key=api_key)

# Global cache for geocoded locations
geocode_cache = {}

def geocode_address(address):
    # Try to fetch coordinates from the cache first
    if address in geocode_cache:
        latitude, longitude = geocode_cache[address][0], geocode_cache[address][1]
        return latitude, longitude

    else:
        # No coordinates found; query Google Maps API
        address_string = f"{address}, Norman, Oklahoma, USA" 
        api_result = gmaps.geocode(address_string)
        
        if api_result:
            latitude = api_result[0]['geometry']['location']['lat']
            longitude = api_result[0]['geometry']['location']['lng']
            
            # Save the new coordinates in the cache
            geocode_cache[address] = (latitude, longitude)
            return latitude, longitude
        else:
            # Handle the case where the API returns no results
            print(f"Geocoding API returned no results for address: {address_string}")
            return None, None
