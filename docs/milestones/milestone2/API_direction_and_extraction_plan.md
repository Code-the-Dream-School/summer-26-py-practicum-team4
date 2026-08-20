# API direction and extraction plan
Our team has selected the OpenWeather Historical Air Pollution API as the primary API for City Air Tracker. It provides historical air pollution information for geographic coordinates and returns an overall AQI value along with concentrations of several pollutants. Data is available from November 27, 2020.

## OpenWeather API
By using OpenWeather API information, users can view and compare historical air-quality conditions for a selected city over time. The API provides measurements for CO, NO, NO₂, O₃, SO₂, PM2.5, PM10, and NH₃, as well as OpenWeather's own AQI value. This will be useful for calculating the US AQI. Extracted data will initially be stored as a raw JSON response.

The historical Air Pollution endpoint is:
https://api.openweathermap.org/data/2.5/air_pollution/history
Request parameters are:
- lat — latitude of the selected city
- lon — longitude of the selected city
- start — beginning of the requested period 
- end — end of the requested period
- appid — OpenWeather API key

## Geocoding API
In addition to the Air Pollution Historical API, we will use the Geocoding API  to convert a user-entered location into geographic coordinates. This will not require us to store the data or search for the coordinates ourselves. A user will be able to enter a city name and code; the Geocoding API will return matching locations containing city name, lat, lon, country, and state if it is in the US. Lon and lat will then be passed along to the Air Pollution API. 

The endpoint for the Geocoding API: 
https://api.openweathermap.org/geo/1.0/direct
Request parameters are:
- q — the location to search for, such as a city name, state code, and country code
- appid — the OpenWeather API key
- limit — optional maximum number of matching locations to return

## API storage and Errors
Each of us will have our personal API keys that will be stored locally in the .env file, which is included in .gitignore

Errors that should be anticipated:
invalid, inactive, or unauthorized API key
missing or invalid latitude and longitude values
an invalid start or end date
a requested period outside the available historical range
an empty result from the API

