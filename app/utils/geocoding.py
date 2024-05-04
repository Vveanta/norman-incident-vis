import googlemaps # type: ignore
import configparser

# Read API key from config file
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['google_maps']['GOOGLE_API_KEY']
gmaps = googlemaps.Client(key=api_key)

# Global cache for geocoded locations
geocode_cache = {}

def geocode_address(address):
    
    # Try to fetch coordinates from the database first
    if address in geocode_cache:
        latitude = geocode_cache[address][0]
        longitude = geocode_cache[address][1]
        return latitude,longitude

    else:
        # No coordinates found; query Google Maps API
        address_string = f"{address}, Norman, Oklahoma, USA" 
        api_result = gmaps.geocode(address_string)[0]
        latitude = api_result['geometry']['location']['lat']
        longitude = api_result['geometry']['location']['lng']
        
        # Save the new coordinates to the database
        # Save the coordinates in the cache
        geocode_cache[address] = (latitude, longitude)
        return latitude, longitude