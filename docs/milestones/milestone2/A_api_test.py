# I have added the city's dataset that was avaliable on the OpenWeather website.
# It is looking for the cityes the user typed(for now in therminal) and if found taking lat and lon from there.
# The dataset with all city info is also located at the shared Google Folder

from dotenv import load_dotenv
import json
import os
import requests
from datetime import datetime, timezone
load_dotenv()

# Getting API key
API_KEY = os.getenv("MY_API_KEY")
if not API_KEY:
    raise ValueError("MY_API_KEY is missing")

#Loading file with city's ID
def load_cities(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Finding the city user will request
def find_city(cities_file, city_name):
    city_name = city_name.strip().lower()
    for record in cities_file:
        if record["city"]["name"].lower() == city_name:
            return record
    return None

# Api request
def get_data(city_record, start, end):
    lat = city_record["city"]["coord"]["lat"]
    lon = city_record["city"]["coord"]["lon"]
    url = "https://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {
        "lat": lat,
        "lon": lon,
        "start": start,
        "end": end,
        "appid": API_KEY
    }
    response = requests.get(url,params=params,timeout=10)
    response.raise_for_status()
    return response.json()



#TESTING the API(testing for existance of the city/errors are not final):

cities = load_cities("docs/milestones/milestone2/data/city_info.json")

# for now asking for a city in the therminal
user_city = input("Enter city name: ")

city = find_city(cities, user_city)
if city is None:
    print(f"City '{user_city}' was not found in the database. Please check if spelling is correct spelling.")
else:
    print(f"{user_city} has been found")

    # dates for July only
    start = int(datetime(2026, 7, 1, tzinfo=timezone.utc).timestamp())
    end = int(datetime(2026, 8, 1, tzinfo=timezone.utc).timestamp())

    #trying to get an API
    try:
        data = get_data(city,start,end)
        print("API request successful!")
    except requests.exceptions.RequestException as error:
        print("API request failed:")
        print(error)