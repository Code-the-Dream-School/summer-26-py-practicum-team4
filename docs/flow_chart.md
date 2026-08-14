# City Air Tracker Target Diagram 2

'''mermaid

flowchart TD
	A(["Pipeline Start"]) ==> B(["City Configuration <br/> from PostgreSQL city table/data"])
	B ==> Load[[" Data Log running: Cities Loaded"]]
	Load ==> Ex[(" Extract Air Pollution data for a selected time and specific date.<br/> Pull AQI data from Openweather")]
	Ex ==> Write[["Write raw data to the PostgreSQL raw table."]]
	Write ==> Load2[/"Log: rows extracted per city"/]
	Load2 ==> Transf[("Transform Step 1: Clean the data , handle any Nan, data types.")]
	Transf ==> Transf2[["Transform Step 2: Add AQI column with color category"]]
	Transf2 ==> Write2[("Load all transformed data to PostgreSQL")]
	Write2 ==> Load3[["Loading finished running , row counts"]]
	Load3 ==> OK(["Run complete , data ready for the dashboard"])
	OK ==> V1{{"Diagram: AQI changes over time range and specific date"}}
	OK -.-> V2{{"AI summary of air quality ona selected date and time"}}
	Ex -.->|API error| ERR[("Retry limited reached")]
	ERR -.-> |no| Ex
	ERR -.-> |yes| Fail(["Log error : Skip city and run the pther cities or stop run"])
	Transf -.-> |invalid data| FAIL
	Write2 -.-> |Dashboard ERROR| FAIL
'''