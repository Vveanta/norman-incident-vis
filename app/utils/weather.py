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