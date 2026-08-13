## Product and data pipeline summary

City Air Tracker will provide information about historical air-quality data presented using the U.S. AQI scale and its corresponding color categories. In the extract stage, the application will retrieve pollutant concentration values for five selected cities for a specified date or time range. The extraction process will use each city's latitude and longitude, the requested start and end dates, and the OpenWeather API. 

The data will be stored in shared documents and transformed into PostgreSQL, storing useful information from the API. Stored data will be cleaned and transformed by handling missing values, correcting data types, and calculating a U.S.-based AQI with its corresponding colors. Additional aggregated tables may also be created to summarize air-quality conditions by city, date, or time period.

The prepared data will be presented in the dashboard. Users will be able to select a city and date or date range, view calculated U.S. AQI values and pollutant measurements, and see changes in air quality over time through charts.
