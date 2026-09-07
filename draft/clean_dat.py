import json
import pandas as pd
from pathlib import Path
import pandas as pd

# For test I used the data collected from Madrid. Data only includes a month of July 2026


# The data that is required to pass to this function is json file, name of the city and folder where the csv file will be stored
def clean_data(data_path, city_name, output_folder):
    #1. Open JSON file
    with open(data_path, "r") as file:
        data = json.load(file)

    # 2.Convert JSON to DataFrame
    df = pd.json_normalize(data["list"])

    # 3.Changing column names
    df.columns = (df.columns.str.replace("components.", "", regex=False).str.replace("main.", "", regex=False))
    required_columns = ["dt","aqi","co","no","no2","o3","so2","pm2_5","pm10","nh3"]

    # 4.Checking all columns exist
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # 5.Convert values to numeric
    for column in required_columns:
        df[column] = pd.to_numeric(df[column],errors="coerce")

    # 6.Remove rows containing NA
    df = df.dropna(subset=required_columns)

    # 7.Remove invalid AQI
    df = df[df["aqi"].isin([1, 2, 3, 4, 5])]

    # 8. Remove rows with negative pollutant values
    df = df[(df[required_columns] >= 0).all(axis=1)]

    # 9.Convert time to the right format and remove ones that couldn't be converted
    df["datetime"] = pd.to_datetime(df["dt"],unit="s",utc=True,errors="coerce")
    df = df.dropna(subset=["datetime"])

    # 10.Remove duplicate observations
    df = df.drop_duplicates(subset=["datetime"],keep="first")

    # 11.Sort
    df = df.sort_values("datetime")

    # 12.Add city name
    df["city"] = city_name

    # 13.Add coordinates
    coordinates = data.get("coord", {})
    df["latitude"] = coordinates.get("lat")
    df["longitude"] = coordinates.get("lon")

    # 14.Rearrange columns
    df = df[
        [
            "city",
            "latitude",
            "longitude",
            "datetime",
            "aqi",
            "co",
            "no",
            "no2",
            "o3",
            "so2",
            "pm2_5",
            "pm10",
            "nh3"
        ]
    ]

    # 15. Reset index
    df = df.reset_index(drop=True)

    # 16.Create CSV file
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    safe_city_name = city_name.lower().replace(" ", "_")
    csv_path = output_folder / f"{safe_city_name}_air_pollution.csv"

    # 18.Save
    df.to_csv(csv_path, index=False)
    return df

# Calling the function:
# clean_data("draft/data/madrid_data.json",'Madrid', 'draft/data')