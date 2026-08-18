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




def userInput():
    # Prompt user to enter their desired location. 
    # Returns a Tuple of Strings (city, state, country)

    city = input("Enter city name: ")
    state = input("Enter 2-letter state code: ")
    country = input("Enter country name: ")
    
    return city, state, country
    
# Grab the latitude and longitude codes from the available geocoding api
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

"""

Helper function to get start and end dates user wants
    def get_date():
        
        Prompt user for date (YYYY-MM-DD)
        convert text to UTC timestamp
        return timestamp

Use helper function to get start/end dates with error catch

    start = get_date("Enter start date")
    end = get_date("Enter end date")


        Catch Errors
            If start > end then:
                print Error message
            else if: (do we want to limit date range?)
                print error: Range cannot exceed LIMIT days
"""
def get_pollution_data():

# Retrieves air pollution data from OpenWeather using the coordinates obtained from the Geocoding function.

    # Fetch coordinates dynamically from geocode helper function
    latitude, longitude = get_latitude_longitude()

    
    # Construct OpenWeather Air Pollution API
    pollution_api = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={API_KEY}"
    response = requests.get(pollution_api)

    if response.status_code == 200:
        print("Request was successful. Retrieving pollution data")
        data = response.json()

        # verify data was retrieved. 
        if data: 
            print(data)
        else:
            print("No pollution data for that city was found.")
    else:
            print(f"Error Status code: {response.status_code}")


# Script trigger
get_pollution_data()

