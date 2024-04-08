# CIS6930 Assignment 2 - Augmenting Data
- **Name:** Vedansh Mahehswari
- **Email:** maheshwariv@ufl.edu

## Overview
This project is an extension of Assignment 0, focusing on data augmentation of records extracted from public police department PDF files. The main objective is to enhance the structured data for analysis and downstream processing, considering fairness and bias. The augmentation involves enriching each record with additional attributes like weather, location rank, and incident rank.

## Installation and Usage
To run this project, ensure you have Python installed on your system (version 3.11 or later recommended). The project uses several external libraries including `pandas`, `googlemaps`, `openmeteo_requests`, and `pytest` for testing.

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install dependencies using Pipenv:
   ```bash
   pipenv install
   ```
4. Activate the virtual environment:
   ```bash
   pipenv shell
   ```
5. To run the main program with a URLs file, use the following command:
   ```bash
   pipenv run python assignment2.py --urls files.csv
   ```
   Replace `files.csv` with your actual file containing URLs to the incident PDFs.

## Data Augmentation Process
The data augmentation is performed on the structured data generated from Assignment 0. The original data schema includes:
```
CREATE TABLE IF NOT EXISTS incidents (
    incident_time TEXT,
    incident_number TEXT,
    incident_location TEXT,
    nature TEXT,
    incident_ori TEXT
);
```

For each incident record, the following attributes are added:

- **Day of the Week**: Numeric value (1-7), mapping Sunday to 1 and Saturday to 7.
- **Time of Day**: Hour of the incident (0-24).
- **Weather**: WMO CODE indicating the weather condition at the time and location of the incident.
- **Location Rank**: Frequency-based ranking of incident locations.
- **Side of Town**: Orientation-based classification (N, S, E, W, NW, NE, SW, SE) relative to the center of town.
- **Incident Rank**: Frequency-based ranking of incident natures.
- **Nature**: Direct text from the source record.
- **EMSSTAT**: Boolean indicating if the Incident ORI was `EMSSTAT` or a subsequent record within two entries shares the same time and location with an `EMSSTAT` ORI.

## Data Augmentation Details

The project's main goal is to enhance the structured dataset produced in Assignment 0 by adding various attributes to each record. This section of the README explains how each attribute is determined and integrated into the dataset.

### Day of the Week and Time of Day
To add the "Day of the Week" and "Time of Day" attributes, we utilized Python's `datetime` module. The `datetime.strptime` function is used to convert the `incident_time` from a string to a `datetime` object, which allows us to extract both the day of the week and the hour of the incident. The `isoweekday()` method returns the day of the week as an integer (1 for Monday, 7 for Sunday), and the `hour` attribute of the `datetime` object provides the hour of the day the incident occurred.

### Weather
The "Weather" attribute is determined by querying the Open-Meteo API with the latitude, longitude, and date of the incident. The response includes historical weather data, from which we extract the WMO weather code corresponding to the incident's hour. This process is encapsulated within the `fetch_weather_data` function.

### Location Rank and Incident Rank
Both "Location Rank" and "Incident Rank" are calculated based on the frequency of occurrences of each location and incident nature within the dataset. The `calculate_frequencies` function counts occurrences, and the `assign_ranks` function assigns a rank based on frequency, handling ties appropriately. The ranking is determined after converting the dataset into a list of dictionaries for easy manipulation.

### Side of Town
To determine the "Side of Town," we first geocode the incident location to obtain latitude and longitude using the Google Maps API. With these coordinates, we calculate the bearing from the center of town (specified as 35.220833, -97.443611) using the `calculate_bearing` function. Based on the bearing, the `determine_side_of_town` function categorizes the incident into one of eight directional classifications (N, S, E, W, NW, NE, SW, SE).

### Nature
The "Nature" attribute is a direct copy of the incident's nature from the source record, representing the type or category of the incident.

### EMSSTAT
Determining the "EMSSTAT" boolean involves checking if the incident's ORI is 'EMSSTAT' or if any of the subsequent two records share the same time and location and have an ORI of 'EMSSTAT'. This logic is implemented in the `check_emsstat` function, which iterates over the dataset to check each incident against these criteria.

## Augmentation Process Implementation
The `augment_data` function orchestrates the augmentation process. It retrieves incidents from the database, iterates through each incident, and applies the above-described methods to add the new attributes. Finally, it compiles the augmented incidents into a new dataset ready for further processing or analysis.

## Testing

To ensure the reliability and correctness of our data augmentation process, we have implemented a series of tests located in the `tests/` directory. These tests cover critical functionality such as geocoding, weather data retrieval, and directional calculations:

- **`test_direction.py`**: Verifies that the `determine_side_of_town` function accurately calculates the side of town based on given latitude and longitude values.
- **`test_geo.py`**: Tests the `geocode_address` function to ensure it correctly translates an address into latitude and longitude, including scenarios where addresses are not previously cached.
- **`test_weather.py`**: Confirms that the `fetch_weather_data` function retrieves accurate weather data for specified dates and locations.

To run all tests and validate the functionality:

```bash
pipenv run python -m pytest
```

## Known Bugs and Assumptions
- **Geocoding Limitations**: The accuracy of geocoding may vary, and the Google Maps API has rate limits.
- **Weather API Call Efficiency**: Due to retrieving weather data for each incident, significant delays and inefficiencies occur. A caching mechanism for weather data could significantly improve performance by reducing redundant API calls for incidents in close temporal and spatial proximity. Could implement this only if there was a way to knwo which all areas comes under the same weather conditions.
- **Time of Day Calculation**: Implemented to range from 0-23 hours, using the floor of the incident time, in alignment with the assignment's requirement for a numeric code from 0 to 24.

## External Resources
- Google Maps API for geocoding.
- Open-Meteo API for historical weather data.

## Contribution and Acknowledgments
This project was developed independently. External resources mentioned above were consulted for specific functionalities. Any further contributions or use of third-party code are cited within the code comments.





