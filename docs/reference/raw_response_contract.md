# Raw Response Contract

**Purpose:** This explains what a raw OpenWeather record looks like when it is saved, before any cleaning or changes.

**Covers:** The Geocoding (direct) and Air Pollution History endpoints.

**Status:** Sprint 2 deliverable, handed to Sprint 3 for storage work.

## 1. What the Raw Layer Is

When the pipeline calls OpenWeather, it saves the response exactly as it arrives, plus a few extra details about the request. The data is not changed at this step. That way the original copy is always kept, in case something needs to be fixed or re-run later.

Each raw record keeps track of:

1. What was requested (city, coordinates, endpoint, and time range).
2. When the request happened and whether it worked (times and status code).
3. What came back (the OpenWeather JSON response).

## 2. The Two Calls

The pipeline reads `cities.csv`, then makes two kinds of call. Both produce raw records, and both use the same fields.

| Step | Endpoint | Sends | Gets back |
| --- | --- | --- | --- |
| 1. Find the location | `geo/1.0/direct` | City, state, country | Latitude and longitude |
| 2. Get the readings | `air_pollution/history` | Latitude, longitude, time range | Hourly pollutant readings |

Geocoding results are saved too, even though they are easy to look up again. If a city's coordinates change between runs, the raw records show when and why.

| Endpoint | Base URL |
| --- | --- |
| Geocoding | `http://api.openweathermap.org/geo/1.0` |
| Air pollution | `https://api.openweathermap.org/data/2.5` |

## 3. Raw Record Fields

Each raw record is one row. The `payload` field holds the JSON from the API. The other fields are extra info the pipeline adds.

| Field | Type | Required? | Description |
| --- | --- | --- | --- |
| `raw_id` | Text | Yes | Unique ID for this record. |
| `city_id` | Text | Yes | Which city this is for, matching `cities.csv` (`US_PHX_01`). Geocoding records have it too, so coordinates can be traced back to the input row. |
| `api` | Text | Yes | Which provider the data came from (`openweather`). Here so a second provider can be added later without confusion. |
| `endpoint` | Text | Yes | Which endpoint was called (`geo/1.0/direct` or `air_pollution/history`). |
| `request_url` | Text | Yes | The full URL that was called, with the API key removed. |
| `request_params` | JSON | Yes | The query parameters that were sent, with `appid` removed. |
| `lat` | Number | Air pollution only | Latitude used in the request. Empty for geocoding, where coordinates are the answer, not the question. |
| `lon` | Number | Air pollution only | Longitude used in the request. Empty for geocoding. |
| `window_start` | Integer | Air pollution only | Start of the time range, in Unix seconds (UTC). Empty for geocoding. |
| `window_end` | Integer | Air pollution only | End of the time range, in Unix seconds (UTC). Empty for geocoding. |
| `http_status` | Integer | Yes | Status code from OpenWeather (`200`). |
| `payload` | JSON | Yes | The response from OpenWeather, saved as-is. |
| `error` | Text | Yes | Empty when the call worked. Otherwise the error text. |

### Rules for these fields

| Rule | What to do | Why |
| --- | --- | --- |

| Never store the API key | Strip `appid` before building `request_url` and before storing `request_params`. | The key is a secret. A key in a raw record is a review blocker, not a cleanup task. |

| Save failed calls too | Write the record with the status code, whatever body came back (or empty), and a filled-in `error`. | If failures are dropped, a gap in the data looks the same whether OpenWeather had no readings or the call fell over. |

| Do not edit the payload | Save it as-is, even if it looks wrong. | The raw code is the original copy. Fixes belong in transform. |

### Two clocks

Mixing these up is the most common bug in this layer.

| Fields | Whose clock | Stored as |
| --- | --- | --- |
| `requested_at`, `fetched_at` | Ours | Timezone-aware UTC timestamp |
| `window_start`, `window_end`, `payload.list[].dt` | OpenWeather's | Integer, Unix seconds (UTC) |

Leave the OpenWeather values as integers here. Converting them is the transform layer's job.

## 4. What's Inside `payload`

The `payload` is saved exactly as OpenWeather sends it. The shape is different for each endpoint.

| Endpoint | Payload shape |
| --- | --- |
| `geo/1.0/direct` | JSON **array** of matches. Can be empty. |
| `air_pollution/history` | JSON **object** with `coord` and `list`. |

### 4.1 Geocoding request

| Field | Type | Required? | Description |
| --- | --- | --- | --- |
| `q` | Text | Yes | City name, state code (US only), and ISO 3166 country code, separated by commas. |
| `limit` | Integer | No | How many results to return, up to 5. |
| `appid` | Text | Yes | API key. Stripped before storage. |

### 4.2 Geocoding payload

An empty array is a normal `200` response. It means nothing matched. Code that assumes `payload[0]` exists will break on a typo in `cities.csv`.

| Field | Type | Always there? | Description |
| --- | --- | --- | --- |
| `[].name` | Text | Yes | Name of the matched location. |
| `[].lat` | Number | Yes | Latitude of the match. |
| `[].lon` | Number | Yes | Longitude of the match. |
| `[].country` | Text | Yes | ISO 3166 country code. |
| `[].state` | Text | No | State, where available. Missing from many non-US results. |
| `[].local_names` | Object | No | The name in other languages, keyed by language code. Also holds the internal keys `ascii` and `feature_name`. |

### 4.3 Air pollution request

Check that `start` is less than or equal to `end` before calling.

| Field | Type | Required? | Description |
| --- | --- | --- | --- |
| `lat` | Number | Yes | Latitude, from the geocoding step. |
| `lon` | Number | Yes | Longitude, from the geocoding step. |
| `start` | Integer | Yes | Start of range, in Unix seconds (UTC). |
| `end` | Integer | Yes | End of range, in Unix seconds (UTC). |
| `appid` | Text | Yes | API key. Stripped before storage. |

### 4.4 Air pollution payload

An empty `list` is a normal response for a range with no coverage.

| Field | Type | Description |
| --- | --- | --- |
| `coord` | Array | The coordinates, as `[lat, lon]`. Other OpenWeather endpoints return an object here instead. |
| `list` | Array | One item for each time sample. Length varies with the range requested. |
| `list[].dt` | Integer | Time of the reading, in Unix seconds (UTC). |
| `list[].main.aqi` | Integer | Air Quality Index (`1` = Good to `5` = Very Poor). |
| `list[].components` | Object | Pollutant amounts in µg/m³ (`co`, `no`, `no2`, `o3`, `so2`, `pm2_5`, `pm10`, `nh3`). |

| `aqi` | Category |
| --- | --- |
| 1 | Good |
| 2 | Fair |
| 3 | Moderate |
| 4 | Poor |
| 5 | Very Poor |

See `reference/openweather_environmental_api_fields_reference.md` for the full list of payload fields.

## 5. Sample Records

All three samples are for Phoenix, AZ, from the same run.

### 5.1 Geocoding

```json
{
  "raw_id": "raw_geo_0042",
  "city_id": "US_PHX_01",
  "api": "openweather",
  "endpoint": "geo/1.0/direct",
  "request_url": "http://api.openweathermap.org/geo/1.0/direct?q=Phoenix,AZ,US&limit=5",
  "request_params": {
    "q": "Phoenix,AZ,US",
    "limit": 5
  },
  "lat": null,
  "lon": null,
  "window_start": null,
  "window_end": null,
  "requested_at": "2026-08-14T09:03:11Z",
  "fetched_at": "2026-08-14T09:03:12Z",
  "http_status": 200,
  "payload": [
    {
      "name": "Phoenix",
      "local_names": {
        "en": "Phoenix",
        "es": "Phoenix",
        "ja": "フェニックス",
        "ascii": "Phoenix",
        "feature_name": "Phoenix"
      },
      "lat": 33.4484,
      "lon": -112.0740,
      "country": "US",
      "state": "Arizona"
    }
  ],
  "error": null
}
```

### 5.2 Air pollution history

```json
{
  "raw_id": "raw_aqi_0117",
  "city_id": "US_PHX_01",
  "api": "openweather",
  "endpoint": "air_pollution/history",
  "request_url": "https://api.openweathermap.org/data/2.5/air_pollution/history?lat=33.4484&lon=-112.074&start=1704067200&end=1704153600",
  "request_params": {
    "lat": 33.4484,
    "lon": -112.0740,
    "start": 1704067200,
    "end": 1704153600
  },
  "lat": 33.4484,
  "lon": -112.0740,
  "window_start": 1704067200,
  "window_end": 1704153600,
  "requested_at": "2026-08-14T09:03:12Z",
  "fetched_at": "2026-08-14T09:03:14Z",
  "http_status": 200,
  "payload": {
    "coord": [33.4484, -112.0740],
    "list": [
      {
        "dt": 1704067200,
        "main": { "aqi": 3 },
        "components": {
          "co": 480.652,
          "no": 12.514,
          "no2": 31.876,
          "o3": 2.945,
          "so2": 8.107,
          "pm2_5": 24.663,
          "pm10": 29.881,
          "nh3": 1.472
        }
      },
      {
        "dt": 1704070800,
        "main": { "aqi": 4 },
        "components": {
          "co": 534.058,
          "no": 18.239,
          "no2": 36.590,
          "o3": 1.108,
          "so2": 9.655,
          "pm2_5": 38.204,
          "pm10": 44.517,
          "nh3": 1.836
        }
      }
    ]
  },
  "error": null
}
```

### 5.3 Failed call

```json
{
  "raw_id": "raw_aqi_0118",
  "city_id": "US_PHX_01",
  "api": "openweather",
  "endpoint": "air_pollution/history",
  "request_url": "https://api.openweathermap.org/data/2.5/air_pollution/history?lat=33.4484&lon=-112.074&start=1704153600&end=1704240000",
  "request_params": {
    "lat": 33.4484,
    "lon": -112.0740,
    "start": 1704153600,
    "end": 1704240000
  },
  "lat": 33.4484,
  "lon": -112.0740,
  "window_start": 1704153600,
  "window_end": 1704240000,
  "requested_at": "2026-08-14T09:03:15Z",
  "fetched_at": "2026-08-14T09:03:16Z",
  "http_status": 429,
  "payload": null,
  "error": "429 Too Many Requests"
}
```

## 6. Fields the Dashboard Will Probably Need

This is not a schema and not a final mapping. The names and units below are OpenWeather's, not ours. Renaming and unit handling belong to the transform layer.

| Source | Field | Why it matters later |
| --- | --- | --- |
| Record | `city_id` | Groups and filters almost every dashboard view. |
| Record | `endpoint`, `fetched_at`, `http_status` | Show how fresh the data is and whether the pull worked. |
| Geocoding payload | `lat`, `lon` | Feed the air pollution calls, and drive any map view. |
| Geocoding payload | `name`, `state`, `country` | Labels for display, and a way to tell same-named cities apart. |
| History payload | `list[].dt` | The time axis for every trend chart. |
| History payload | `list[].main.aqi` | The headline number, and the basis for colour coding. |
| History payload | `list[].components.pm2_5` | The most health-relevant particulate. Likely a default chart. |
| History payload | `list[].components.pm10` | Particulate burden, usually shown next to PM2.5. |
| History payload | `list[].components.o3`, `no2`, `so2`, `co` | Feed into the AQI category, so they explain why AQI moved. |
| History payload | `list[].components.no`, `nh3` | Do not affect AQI directly. Keep them, but expect lower priority. |

## 7. Sprint 3 Handoff

### Storage needs for later

| Need | Detail |
| --- | --- |
| A JSON column for `payload` | PostgreSQL `JSONB` is the expected choice, so the payload can be searched without flattening it first. |

| Room for two payload shapes | Air pollution returns an object, geocoding returns an array. The column and any validation have to allow both. |

| Room for failed calls | `payload` nullable, `error` filled in, `http_status` not `200`. These rows are part of the dataset. |

| Request details kept with the payload | `endpoint`, `request_params`, `requested_at`, `fetched_at`, and `http_status` are what make a record reproducible. |
| A retention decision | How long raw records are kept.

### Open questions

| # | Question | Trade-off |
| --- | --- | --- |

| 1 | PostgreSQL only, or a backup JSON file too? | A backup is cheap insurance if the database is rebuilt, but doubles the write path. If yes, where do we save the JSON file? |

| 2 | Same table for geocoding and air pollution, or separate? | One table keeps the fields consistent. Two tables avoid a lot of empty columns. |

| 3 | How do we split | The data is hourly, so a year+ pull needs a grouping plan and a rule for grouping records back together. |

| 4 | What happens if a city's coordinates change between runs? | Affects whether older air pollution records are still comparable. |

## Related docs

| Doc | What it covers |
| --- | --- |
| `reference/openweather_environmental_api_fields_reference.md` | Full API field reference. |
| `reference/city_input_contract.md` | The rules for the `cities.csv` input that feeds this step. |
