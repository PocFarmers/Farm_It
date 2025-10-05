import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def get_history_info(lat: float, lon: float):
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "daily": ["soil_moisture_0_to_7cm_mean", "soil_temperature_28_to_100cm_mean"],
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_soil_moisture_0_to_7cm_mean = daily.Variables(0).ValuesAsNumpy()
    daily_soil_temperature_28_to_100cm_mean = daily.Variables(1).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
    	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
    	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
    	freq = pd.Timedelta(seconds = daily.Interval()),
    	inclusive = "left"
    )}

    daily_data["soil_moisture_0_to_7cm_mean"] = daily_soil_moisture_0_to_7cm_mean
    daily_data["soil_temperature_28_to_100cm_mean"] = daily_soil_temperature_28_to_100cm_mean

    daily_dataframe = pd.DataFrame(data = daily_data)
    return daily_dataframe
