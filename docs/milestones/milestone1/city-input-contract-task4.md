**Part 4 \- City Input Contract**

**Purpose:**  
The configuration file provides the geographic parameters to query the OpenWeather API without needing to hardcode locations into the pipeline code. The purpose of the city configuration is to store the specific settings, processing rules and behaviors we require for the city. 

**Required fields (?):**   
City\_name  
State\_code  
Country\_code  
Latitude \-\> lat  
Longitude \-\> lon

**Valid Example:**

**{**  
  **"city\_id": "C-101",**  
  **"city\_name": "Seattle",**  
  **"state\_code": "WA",**  
  **"country\_code": "US",**  
  **"lat": 47.6062,**  
  **"lon": \-122.3321**  
**}**

## **Error Handling & Validation Rules**

* **Missing Required Fields:** If `city_id`, `city_name`, `country_code`, `lat`, or `lon` is `null` or missing, return  `INVALID`, log an error, and skip extraction for that entry.  
* **Coordinate Range Check:** If `lat` is not between `-90` and `90`, or `lon` is not between `-180` and `180`, abort processing for that city record.  
* **Duplicate `city_id`:** reduce duplication when running, process only the first occurance

Note:  
To pull data from the OpenWeather API, we need to use longitude and latitude codes. 

**API’s:**

**GeoCoding**  
[https://openweathermap.org/api/geocoding-api?collection=other\#direct](https://openweathermap.org/api/geocoding-api?collection=other#direct)

**Current Pollution Data**  
http://api.openweathermap.org/data/2.5/air\_pollution?lat={lat}\&lon={lon}\&appid={API key}

**Predicted Pollution Data**  
http://api.openweathermap.org/data/2.5/air\_pollution/forecast?lat={lat}\&lon={lon}\&appid={API key}

**Historical Pollution Data**

http://api.openweathermap.org/data/2.5/air\_pollution/history?lat={lat}\&lon={lon}\&start={start}\&end={end}\&appid={API key}

| Parameters |  |  |
| :---- | :---- | :---- |
| lat | required | Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our [Geocoding API](https://openweathermap.org/api/geocoding-api) |
| lon | required | Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our [Geocoding API](https://openweathermap.org/api/geocoding-api) |
| start | required | Start date (unix time, UTC time zone), e.g. start=1606488670 |
| end | required | End date (unix time, UTC time zone), e.g. end=1606747870 |
| appid | required | Your unique API key (you can always find it on your account page under the ["API key" tab](https://home.openweathermap.org/api_keys)) |

**Example of API response**

{  
  "coord":\[  
    50,  
    50  
  \],  
  "list":\[  
    {  
      "dt":1605182400,  
      "main":{  
        "aqi":1  
      },  
      "components":{  
        "co":201.94053649902344,  
        "no":0.01877197064459324,  
        "no2":0.7711350917816162,  
        "o3":68.66455078125,  
        "so2":0.6407499313354492,  
        "pm2\_5":0.5,  
        "pm10":0.540438711643219,  
        "nh3":0.12369127571582794  
      }  
    }  
  \]  
}                 
