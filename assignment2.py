import argparse
import datetime
import pandas as pd
import urllib.request
import os
import urllib.request
import googlemaps # type: ignore
import configparser
import requests
# Global cache for geocoded locations
geocode_cache = {}

# Read API key from config file
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['google_maps']['GOOGLE_API_KEY']
gmaps = googlemaps.Client(key = api_key)
# Function to fetch incident PDFs from a specified URL
def fetch_incidents(url, filename):
    # Set up a user agent to prevent request being blocked
    headers = {'User-Agent': "Mozilla/5.0"}
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    # Write the data to a file
    with open(filename, 'wb') as file:
        file.write(data)

import PyPDF2 # type: ignore
import re
import fitz  # type: ignore # PyMuPDF
# Function to extract incidents from the downloaded PDF
def extract_incidents(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    all_text = ""
    # Extract text from each page
    for page in doc:
        all_text += page.get_text()
    doc.close()
    # Prepare lines for processing
    lines = all_text.split('\n')
    lines = [line.strip() for line in lines]
    # Filter out header and footer lines
    lines = [line for line in lines if 'NORMAN POLICE DEPARTMENT' not in line and "Daily Incident Summary (Public)" not in line and line != "RAMP"]
    incidents = []
    # Regex pattern to identify the date and time format
    date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}')

    i=5
    # Iterate through lines to extract incident details
    while i < len(lines):
        # Use regex to check if the line starts with a date and time
        if i + 3 < len(lines) and date_pattern.match(lines[i]):
            incident_time = lines[i]
            incident_number = lines[i + 1]
            # Default values for missing data
            location = "/"  # Default value
            nature = "/"    # Default value
            incident_ori = "/"  # Default value
            # Logic to handle missing data fields
            if i + 2 < len(lines) and not date_pattern.match(lines[i + 2]):
                if i + 3 < len(lines) and not date_pattern.match(lines[i + 3]):
                    if i + 4 < len(lines) and not date_pattern.match(lines[i + 4]):
                        location = lines[i + 2]
                        nature = lines[i + 3]
                        incident_ori = lines[i + 4]
                        i+=5
                    else:
                        location = lines[i + 2]
                        incident_ori = lines[i + 3]
                        i+=4
                else:
                    incident_ori = lines[i+2]
                    i+=3

            else:
                # Handle cases where either location or nature is missing
                incident_ori = lines[i + (2 if location == "/" else 3)].strip()
                i += (4 if location == "/" or nature == "/" else 5)
            # Add the incident to the list
            incident = {
                'Incident_time': incident_time,
                'Incident Number': incident_number,
                'Location': location,
                'Nature': nature,
                'Incident ORI': incident_ori,
            }
            incidents.append(incident)
        else:
            i += 1  # Increment to avoid infinite loop
    return incidents

import sqlite3
# Function to create the database and table for storing incidents
def create_db(db_path="resources/normanpd.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Reset the table if it exists
    c.execute('DROP TABLE IF EXISTS incidents;')
    # Create the incidents table
    c.execute('''   
                 CREATE TABLE IF NOT EXISTS incidents (
                 incident_time TEXT,
                 incident_number TEXT,
                 incident_location TEXT,
                 nature TEXT,
                 incident_ori TEXT
                 )''')
    conn.commit()
    conn.close()

import sqlite3
# Function to populate the database with incident data
def populate_db(db_path, incidents):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Insert each incident into the database
    for incident in incidents:
        c.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?)", (incident['Incident_time'],incident['Incident Number'], incident['Location'], incident['Nature'], incident['Incident ORI']))
    conn.commit()
    conn.close()

def check_emsstat(incidents, current_index):
    current_incident = incidents[current_index]
    # Check the current incident's ORI directly
    if current_incident['Incident ORI'].startswith('EMSSTAT'):
        return True
    
    # Check the next one or two incidents for the same time, location, and EMSSTAT ORI
    for next_index in range(current_index + 1, min(current_index + 3, len(incidents))):
        next_incident = incidents[next_index]
        if (current_incident['Incident_time'] == next_incident['Incident_time'] and
            current_incident['Location'] == next_incident['Location'] and
            next_incident['Incident ORI'].startswith('EMSSTAT')):
            return True
    return False

def calculate_frequencies(incidents, attribute):
    """
    Calculate the frequencies of a given attribute (location or nature) in the incidents.
    """
    from collections import Counter
    values = [incident[attribute] for incident in incidents]
    frequencies = Counter(values)
    return frequencies

def assign_ranks(frequencies):
    """
    Assign ranks to each unique value based on its frequency, handling ties appropriately.
    """
    # Sort items based on frequency, then by the value itself for consistent ordering
    sorted_items = sorted(frequencies.items(), key=lambda x: (-x[1], x))
    ranks = {}
    current_rank = 1
    for i, (value, freq) in enumerate(sorted_items, start=1):
        # If it's the first item or if the current frequency is different from the previous one,
        # update the current rank to be the current position (i).
        if i == 1 or freq < sorted_items[i-2][1]:
            current_rank = i
        ranks[value] = current_rank
    return ranks

import sqlite3

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
    
import openmeteo_requests # type: ignore
import requests_cache # type: ignore
import pandas as pd
from retry_requests import retry # type: ignore
def fetch_weathercode_using_meteo(latitude, longitude, date, hour):
    # Note: the code block is directly taken from https://open-meteo.com/en/docs/historical-weather-ap

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date,
        "end_date": date,
        "hourly": "weather_code"   
    }
     # Note: the code block is directly taken from https://open-meteo.com/en/docs/historical-weather-ap"
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_weather_code = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["weather_code"] = hourly_weather_code
    # Note: the code block is directly taken from https://open-meteo.com/en/docs/historical-weather-ap

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    return int(hourly_dataframe['weather_code'][hour])

import math

def calculate_angle(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lon = lon2 - lon1
    x = math.cos(lat2) * math.sin(delta_lon)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))
    initial_angle = math.atan2(x, y)
    initial_angle = math.degrees(initial_angle)
    angle = (initial_angle + 360) % 360
    return angle

def calculate_street_position(latitude, longitude):
    CENTER_OF_TOWN_LAT, CENTER_OF_TOWN_LON = 35.220833, -97.443611
    angle = calculate_angle(CENTER_OF_TOWN_LAT, CENTER_OF_TOWN_LON, latitude, longitude)
    if angle >= 337.5 or angle < 22.5:
        return "N"
    elif 67.5 <= angle < 112.5:
        return "E"
    elif 247.5 <= angle < 292.5:
        return "W"
    elif 157.5 <= angle < 202.5:
        return "S"
    elif 22.5 <= angle < 67.5:
        return "NE"
    elif 112.5 <= angle < 157.5:
        return "SE"
    elif 202.5 <= angle < 247.5:
        return "SW"
    elif 292.5 <= angle < 337.5:
        return "NW"


def augment_data(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM incidents')
    incidents = cursor.fetchall()
    # Convert tuple to dict for easier manipulation
    incidents_dicts = [{'Incident_time': i[0], 'Incident Number': i[1], 'Location': i[2], 'Nature': i[3], 'Incident ORI': i[4]} for i in incidents]
    # Calculate frequencies and then ranks for locations and natures
    location_frequencies = calculate_frequencies(incidents_dicts, 'Location')
    nature_frequencies = calculate_frequencies(incidents_dicts, 'Nature')
    # check if frequency code is working
    # for  k, v in location_frequencies.items():
    #     print(f"Name: {k}, Frequency: {v}")
    location_ranks = assign_ranks(location_frequencies)
    nature_ranks = assign_ranks(nature_frequencies)

    # Placeholder for augmented data
    augmented_incidents = []
    for index, incident in enumerate(incidents_dicts):
        incident_time = datetime.datetime.strptime(incident['Incident_time'], "%m/%d/%Y %H:%M")
        # Day of the Week (1=Sunday, 7=Saturday)
        dow = incident_time.isoweekday()
        adow = (dow % 7) + 1
        incident['Day Of The Week'] = adow
        # Time of Day (hour)
        incident['Time Of Day'] = incident_time.hour
        # latitude, longitude = geocode_location(location)  # Assuming implementation
        latitude, longitude = geocode_address(incident['Location'])
        incident['Weather'] = fetch_weathercode_using_meteo(latitude, longitude, incident_time.strftime("%Y-%m-%d"), incident_time.hour)
        incident['Side of Town'] = calculate_street_position(latitude, longitude)
        incident['Location Rank'] = location_ranks[incident['Location']]
        incident['Nature Rank'] = nature_ranks[incident['Nature']]
        incident['EMSSTAT'] = check_emsstat(incidents_dicts, index)
        augmented_incidents.append(incident)
        # print('check2')
    return augmented_incidents
    
def main(urls_file):


    urls = pd.read_csv(urls_file, header=None, index_col=False)
    if not os.path.exists('resources'):
        os.makedirs('resources')
    db_path = "resources/normanpd.db"
    # Create new database (if not exists)
    create_db(db_path)
    for url in urls[0]:
        pdf_filename = "/tmp/incident.pdf"  # Example path, (path to store temporary pdf files)
        # Download data
        
        fetch_incidents(url, pdf_filename)

        # Extract data
        incidents = extract_incidents(pdf_filename)
        # Insert data
        populate_db(db_path, incidents)
    # print('check1')
    augmented_incidents = augment_data(db_path)
    
    # with open('output_txt.txt', 'w') as output_file:
    #     for incident in augmented_incidents:
    #         output_file.write(str(incident) + '\n')
    print("Day of the Week\tTime of Day\tWeather\tLocation Rank\tSide of Town\tIncident Rank\tNature\tEMSSTAT")

    # Iterate through augmented incidents and print each one in the specified format
    for incident in augmented_incidents:
        print(f"{incident['Day Of The Week']}\t"
            f"{incident['Time Of Day']}\t"
            f"{incident['Weather']}\t"
            f"{incident['Location Rank']}\t"
            f"{incident['Side of Town']}\t"
            f"{incident['Nature Rank']}\t"
            f"{incident['Nature']}\t"
            f"{1 if incident['EMSSTAT'] else 0}")
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", type=str, required=True, help="CSV file containing PDF URLs.")
     
    args = parser.parse_args()
    if args.urls:
        main(args.urls)
