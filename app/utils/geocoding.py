import googlemaps
import configparser
import sqlite3
import os

# # for local 
# # Read API key from config file
# config = configparser.ConfigParser()
# config.read('config.ini')
# api_key = config['google_maps']['GOOGLE_API_KEY']

#for deployment server
# Get API key from environment variables
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("No GOOGLE_API_KEY set for Flask application")
gmaps = googlemaps.Client(key=api_key)


# Global cache for geocoded locations
# geocode_cache = {}

def geocode_address(address, db_path="resources/normanpd.db"):
    # Try to fetch coordinates from the cache first
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT latitude, longitude FROM geocodes WHERE location = ?", (address,))
    result = c.fetchone()
    conn.close()

    if result:
        return result[0], result[1]

    else:
        # No coordinates found; query Google Maps API
        address_string = f"{address}, Norman, Oklahoma, USA" 
        api_result = gmaps.geocode(address_string)
        
        if api_result:
            latitude = api_result[0]['geometry']['location']['lat']
            longitude = api_result[0]['geometry']['location']['lng']
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("INSERT INTO geocodes (location, latitude, longitude) VALUES (?, ?, ?)", (address, latitude, longitude))
            conn.commit()
            conn.close()
            # Save the new coordinates in the cache
            # geocode_cache[address] = (latitude, longitude)
            return latitude, longitude
        else:
            # Handle the case where the API returns no results
            print(f"Geocoding API returned no results for address: {address_string}")
            return None, None
