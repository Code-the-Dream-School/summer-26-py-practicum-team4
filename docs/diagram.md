# City Air Tracker Diagram 1

'''mermaid
flowchart TD
		subgraph dev[Target Architecture]
				A[(City Input or Configuration)] ==> id1[/"5 Cities"/] 
		end
		
		subgraph ext[Extract and Store]
				B[("Extract Gegraphic Cities / Air Data Extraction from OpenWeather")] ==> C@{ shape: das, label: "Transform step 1: Show raw API response to the PostgreSQL tables" }
				C -.-> |extraction| B
				C ==> D@{ shape: das, label: "  Data Transform step 2: Have new tables contain AQI classifying ,etc" } 
				D ==> E@{ shape: lin-cyl, label: "PostgreSQL storage: Contain all the dataset" } 
		end
		
		subgraph display["API & Frontend Interface"]
				F@{ shape: win-pane, label: "Dashboard API" } ==> G@{ shape: win-pane, label: "React frontend Full interface" } 
		end
		
		subgraph opt[ Optional Feature]
				H@{ shape: das, label: "AI bot( optional extension)"} 
				I@{ shape: das, label: "Cloud deployment "}
		end
		
		dev ==> ext
		ext ==> display
		dev -.-> opt
		opt -.-> E
'''