import os 
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv 

#====== Loading the key from the .env file ====
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

#====== The two endpoints, Same API key , different cities ====
#First API key is air pollution API 
AIR_POLLUTION_HISTORY_URL = "http://api.openweathermap.org/data/2.5/air_pollution/history"
#Second API key is geocoding API 
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"

#Cities to extract from the API
Cities = [
    {"city": "Madrid", "country": "ES" },
    {"city": "Houston", "state": "TX", "country": "US"},
]
#========= First API call to get the air pollution data for a city =======
#=== data from July 2026, created into unix timestamp for API to call
JULY_START = int(datetime(2026, 7, 1, tzinfo=timezone.utc).timestamp())
JULY_END = int(datetime(2026, 7, 31, 23, 59, 59, tzinfo=timezone.utc).timestamp())

#define function to get the air pollution data fro a city 
def get_air_pollution_history(lat, lon, start, end):
    """Get air pollution historical data for a given latitude and longitude"""
    if start > end:
        raise ValueError("Start date must be before end date")
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "start": start, "end": end}
    response = requests.get(AIR_POLLUTION_HISTORY_URL, params=params, timeout=10)
    response.raise_for_status() #Raise an error if request fails
    return response.json()

#Extract cities, get the coordinates and then get the air pollution
def extract_data(record):
    """Full process for one city, wrapped the raw response"""
    lat, lon = get_coordinates(record["city"], record["country"], record.get("state"))
    raw = get_air_pollution_history(lat, lon, JULY_START, JULY_END)
    return {
        "location": {**record , "lat": lat, "lon": lon},
        "endpoint": AIR_POLLUTION_HISTORY_URL,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "raw_payload": raw,
    }

#========= Second API call to get the coordinates of a city =======
#define function to get the coordinates of a city 
def get_coordinates(city, country, state=None):
    """Turn cities name into longitude and latitude coordinates using OpenWeatherMap API"""
    query = ",".join(part for part in [city, state, country] if part)
    params = {"q": query, "limit": 1, "appid": API_KEY}
    #Get and make the request to the API
    response = requests.get(GEO_URL, params=params, timeout=10)
    response.raise_for_status() #Raise an error if request fails
    results = response.json()
    if not results:
        raise ValueError(f"No coordinates found for {query}")
    return results[0]["lat"], results[0]["lon"]

if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit("OPENWEATHER_API_KEY is not set up , please check the .env file")

    all_results = []
    #loop through the cities and extract the data
    for city in Cities:
        try:
            result = extract_data(city)
            entry = result["raw_payload"]["list"][0]
            print(f"\n{city['city']}, {city['country']} "
            f"lat={result['location']['lat']}, lon={result['location']['lon']})")
            print(f" OPENWEATHER AQI: {entry['main']['aqi']}")
            #loop through the components and print them out
            for pollutant, value in entry["components"].items():
                print(f"{pollutant}: {value}")
                saved_any = True
                #=== trimmed the entries 
                trimmed = {**result, "raw_payload": {**result["raw_payload"],
                                   "list": result["raw_payload"]["list"][:3]}}
            all_results.append(trimmed) #add the trimmed result 
        except Exception as e:
            #add a safe message to avoid printing the API key in case of error 
            safe_msg = str(e).replace(API_KEY, "***") if API_KEY else str(e)
            print(f"Error! Failed for {city['city']}: {safe_msg}")

#store the result 
        if all_results:
            with open("store_results.json", "w") as f:
                json.dump(all_results, f, indent=4)
            print("\nSaved trimmed sample (first 3 entries) to store_results.json")

