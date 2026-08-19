"""
 
This script interacts with the OpenWeather API to dynamically fetch air pollution data
based on user-specified city, state, and country coordinates.
Tested successfully with 'Los Angeles' and 'New York'.
 
 
"""
 
import requests
from prefect import flow,task 
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timezone
 
# Load environment variables from local .env file
load_dotenv()
 
 
# Retrieve OpenWeather API key from environment variables
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    print("No API Key found.")
 
# Load in the json file that contains the sample data
def load_cities(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
 
 
 
# Helper function. Cleans and standarizes the user_city variable found in the ask_for_city function.
 
def find_city(cities_file, city_name):
    city_name = city_name.strip().lower()
    for record in cities_file:
        if record["city"]["name"].lower() == city_name:
            return record
    return None
 
 
# Querys user for city name, checks data and pulls from the local dataset.
def ask_for_city():
    # Load in JSON File
    cities = load_cities("/draft/sprint2_api/data/city_data.json")
 
    #Get User input
    user_city = input("Enter city name: ")
 
    # Grab the JSON File and user's requested city
    city = find_city(cities, user_city)
 
    #Check if City is found in dataset
    if city is None:
        print(f"City '{user_city}' was not found in the database. Please check if spelling is correct spelling.")
        return None
    else:
        print(f"{user_city} has been found")
        return city
 
# Step 1: Try JSON file first
 
def get_coordinates():
    city = ask_for_city()
    if city:
        # Use coordinates from JSON
        latitude = city["city"]["coord"]["lat"]
        longitude = city["city"]["coord"]["lon"]
    else:
        # Fall back to Geocoding API
        latitude, longitude = get_latitude_longitude()
    
    return latitude, longitude
 
 
def userInput():
    city = input("Enter city name: ")
    state = input("Enter 2-letter state code: ")
    country = input("Enter country name: ")
    return city, state, country
 
 
def get_latitude_longitude():
    city_name, state_code, country = userInput()
 
    # Construct Geocoding API endpoint with user inputs and API authentication
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country}&appid={API_KEY}"
 
    response = requests.get(geocode_url)
 
    # Verify the API returned data.
    if response.status_code == 200:
        print("Retrieving coordinates")
        data = response.json()
 
        if data: #Check if list is empty
            latitude = data[0].get('lat')
            longitude = data[0].get('lon')
            print(latitude, longitude)
            return latitude, longitude
        else:
            print("That city was not found.")
    else:
        print(f"Error Status code: {response.status_code}")
 
 
 
# Api request
def get_data(latitude, longitude, start, end):
 
    url = "https://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {
        "lat": latitude,
        "lon": longitude,
        "start": start,
        "end": end,
        "appid": API_KEY
    }
    response = requests.get(url,params=params,timeout=10)
    response.raise_for_status()
    return response.json()
 
 
 
 
# Retrieves air pollution data from OpenWeather using the coordinates obtained from the Geocoding function.

def get_pollution_data():
 
    latitude, longitude = get_coordinates()
 
    if latitude is None or longitude is None:
        print("Error: No latitude or longitude coordinates.")
        return
    
    # dates for July only
    start = int(datetime(2026, 7, 1, tzinfo=timezone.utc).timestamp())
    end = int(datetime(2026, 8, 1, tzinfo=timezone.utc).timestamp())
 
    pollution_data = get_data(latitude, longitude, start, end)
    return pollution_data