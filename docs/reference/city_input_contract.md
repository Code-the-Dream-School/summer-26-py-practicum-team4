# City Input Contract

**Purpose:** Defines `cities.csv`, the file that tells the pipeline which cities to pull data for.

**Covers:** The file's shape, its columns, and what the pipeline does with a row that is missing or wrong.

**Does not cover:** How the file is read, which endpoints get called, or what comes back. See `reference/raw_response_contract.md`.

**Audience:** Engineers building the extract layer, and anyone editing `cities.csv`.

**Status:** Sprint 2 contract. No implementation this sprint. Four open questions still outstanding — see section 7.

## 1. Why this file exists

The pipeline needs a list of cities. Without a config file, that list lives in the code, and adding a city means a code change, a review, and a deploy.

`cities.csv` moves the list out of the code. It is the only place a city is defined, and `city_id` from this file is what every downstream record is keyed on. A raw record with `city_id` of `US_PHX_01` means nothing unless that row exists here.

The file answers one question: **which places, and what do we call them?** It does not carry schedules, time ranges, or API settings.

## 2. Format and location

| Item | Decision |
| --- | --- |
| Format | CSV, UTF-8, one row per city |
| Header row | Required, exact column names, lowercase |
| Filename | `cities.csv` |
| Location | Not decided — see open question 4 |

The Part 4 draft showed a JSON object per city. This contract uses CSV instead, because the raw response contract already names `cities.csv` as the input and Sprint 3 will build against that. **Judgement call.** The column list below works either way if the team flips it.

## 3. Columns

| Column | Type | Required? | Description |
| --- | --- | --- | --- |
| `city_id` | Text | Yes | Our permanent ID for this city. Format `<COUNTRY>_<CITY>_<NN>`, e.g. `US_PHX_01`. Must be unique in the file. Never reused, never renamed. |
| `city_name` | Text | Yes | City name as OpenWeather knows it, e.g. `Phoenix`. Sent in the geocoding `q` parameter. |
| `state_code` | Text | US rows only | Two-letter US state code, e.g. `AZ`. Empty for every non-US row — OpenWeather only supports state codes for US locations. |
| `country_code` | Text | Yes | ISO 3166-1 alpha-2, uppercase, e.g. `US`, `GB`. |
| `lat` | Number | No | Manual latitude override. Normally empty. |
| `lon` | Number | No | Manual longitude override. Normally empty. |

### Why `lat` and `lon` are not required

The Part 4 draft listed them as required. **I'd push back on that.** The pipeline's first step is a geocoding call whose entire job is to turn city, state, and country into coordinates. If every row already has coordinates, that call is dead code, and adding a city means looking up coordinates by hand.

They are here as an **override** for the case where geocoding returns the wrong place or no match at all — an ambiguous city name, or a location OpenWeather does not have. When `lat` and `lon` are filled in, the pipeline skips geocoding for that row and uses them directly.

This is the one decision in this document I would most like a second opinion on. See open question 1.

## 4. A valid file

```csv
city_id,city_name,state_code,country_code,lat,lon
US_PHX_01,Phoenix,AZ,US,,
US_SEA_01,Seattle,WA,US,47.6062,-122.3321
GB_LON_01,London,,GB,,
```

Three rows, three shapes:

| Row | What happens |
| --- | --- |
| `US_PHX_01` | Geocoded. Sent as `q=Phoenix,AZ,US`. |
| `US_SEA_01` | Coordinates already present. Geocoding is skipped. |
| `GB_LON_01` | Geocoded. Sent as `q=London,GB` — no state segment, because `state_code` is empty. |

Note the empty trailing commas on rows 1 and 3. Every row has all six fields. An empty field is an empty string, not a missing one.

## 5. Rules for missing or invalid values

The unit of failure is the **row**, not the run. One bad city is skipped; the other cities still get pulled.

| Situation | What the pipeline does | Why |
| --- | --- | --- |
| `city_id`, `city_name`, or `country_code` is empty | Mark the row INVALID, log an error with the line number and whatever `city_id` was there, skip the row, keep going. | A city with no ID cannot be joined to anything downstream. A city with no name or country cannot be geocoded. |
| `lat` outside -90 to 90, or `lon` outside -180 to 180 | Mark INVALID, log an error, skip the row. | OpenWeather will reject it or return the wrong place. Failing here is cheaper than debugging it later. |
| Only one of `lat` / `lon` is filled in | Mark INVALID, log an error, skip the row. | Half a coordinate is almost always a typo or a bad paste, not an intentional override. |
| Both `lat` and `lon` empty | Valid. Geocode the row. | This is the normal case. |
| Duplicate `city_id` | Use the first occurrence, log a warning, skip the rest. | Team's decision. See the note below. |
| `state_code` filled in on a non-US row | Drop it from the `q` string, log a warning, keep the row. | OpenWeather only accepts state codes for US locations. **Judgement call** — the alternative is to reject the row. |
| `state_code` empty on a US row | Valid, but geocoding may match the wrong state. Log a warning. | There are US cities named Portland, Springfield, and Columbus in several states each. |
| File missing, empty, or header does not match | **Stop the run.** Do not process anything. | This is a config error, not a data error. Running against a truncated file silently produces a partial dataset that looks complete. |

Values are trimmed of leading and trailing whitespace before any of these checks run. `country_code` and `state_code` are uppercased.

**On duplicate `city_id`:** taking the first occurrence quietly is the team's rule as written, and this document follows it. **I'd push back on it.** Two rows with the same ID means someone edited the file wrong, and the second row is silently dropped — which looks identical to that city never having been added. If you keep this rule, the warning log is the only thing standing between that mistake and a confused engineer three weeks later, so make the warning loud.

## 6. Things that bite

**An empty CSV field is `""`, not `None`.** Every row has every column. Validation that checks `if value is None` will pass on a blank city name. Check for empty strings.

**`0,0` is inside the valid range.** It is also in the Atlantic Ocean, and it is what you get when a spreadsheet fills blanks with zeros. The range check will not catch it. Treat a row with `lat=0` and `lon=0` as suspicious unless someone deliberately wants Null Island.

**A comma in `city_name` breaks the geocoding query.** `q` is comma-separated, so `Washington, D.C.` becomes three segments instead of one. CSV quoting keeps the file parseable but does not fix the API call. Use a name without commas, or set `lat`/`lon` manually.

**`city_id` is permanent.** It is stamped into every raw record. Renaming `US_PHX_01` to `US_PHOENIX_01` orphans every record already stored under the old ID. Add a new row instead, or plan a migration.

**A valid row can still find nothing.** Geocoding returns HTTP 200 with an empty array when the city does not match. That is not caught by this contract — nothing here is wrong with the row. It is handled in the raw layer; see `reference/raw_response_contract.md`, section 4.2.

## 7. Open questions

| # | Question | Trade-off |
| --- | --- | --- |
| 1 | Are `lat` / `lon` optional overrides, or required for every row? | Optional keeps the geocoding step meaningful and makes adding a city a one-line edit. Required removes a network call and a failure mode, but makes the geocoding step pointless and pushes coordinate lookup onto whoever edits the file. This document assumes optional. |
| 2 | Which `city_id` format — `US_PHX_01` or `C-101`? | The raw response contract's samples already use `US_PHX_01`, and it is readable in a log line. `C-101` is shorter but tells you nothing. This document assumes `US_PHX_01`. Sprint 3 storage work should not start until this is settled. |
| 3 | CSV or JSON? | CSV is easier to edit and diff, and matches the `cities.csv` name already in use. JSON handles nested per-city settings if we ever add them. This document assumes CSV. |
| 4 | Where does the file live, and who edits it? | In the repo means every city change is reviewed but needs a deploy. Outside the repo means faster edits and no review. Also decides whether "file missing" is even possible. |

Not asked and not answered: whether this file will later carry per-city settings such as history time ranges or pull frequency. If it will, question 3 matters more than it currently looks.

## Related docs

| Doc | What it covers |
| --- | --- |
| `reference/raw_response_contract.md` | What the pipeline stores after calling OpenWeather with these cities. |
| `reference/openweather_environmental_api_fields_reference.md` | Full API field reference. |
| [OpenWeather Geocoding API](https://openweathermap.org/api/geocoding-api) | Vendor docs for the `q` parameter and the direct geocoding response. |
