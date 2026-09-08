from dash import Dash, dcc, html, Input, Output, State, dash_table

import plotly.express as px

import pandas as pd

import os

import psycopg

from dotenv import load_dotenv

from google import genai

from pathlib import Path


#====== Load

load_dotenv()


def get_connection():

    return psycopg.connect(

        host=os.getenv("DB_Host"),

        port=os.getenv("DB_Port"),

        dbname=os.getenv("DB_Name"),

        user=os.getenv("DB_USER"),

        password=os.getenv("DB_PASSWORD"),

        sslmode="require"

    )


client = genai.Client(

    api_key=os.getenv("GEMINI_API_KEY")

)

MODEL = "gemini-3.6-flash"


#====== AI Functions

def get_ai(prompt):

    try:

        response = client.models.generate_content(

            model=MODEL,

            contents=prompt

        )

        return response.text

    except Exception as error:

        error_message = str(error)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

            return (

                "I'm temporarily unable to answer because "

                "the AI usage limit has been reached. "

                "Please try again later."

            )

        return (

            "I'm sorry, but I'm having trouble connecting "

            "to the AI service right now. Please try again."

        )


#====== Extract Cities

conn = get_connection()

with conn.cursor() as cursor:

    cursor.execute("""

        SELECT city_id, city_name, state

        FROM city_table

        ORDER BY city_name;

    """)

    cities = cursor.fetchall()

conn.close()


#====== Dash Layout

PROJECT_ROOT = Path(__file__).resolve().parents[4]

ASSETS_FOLDER = PROJECT_ROOT / "assets"


app = Dash(

    __name__,

    assets_folder=str(ASSETS_FOLDER)

)


app.layout = html.Div([


#====== Header

    html.Div([

        html.Div([

            html.Img(

                src=app.get_asset_url("logo1.svg"),

                className="logo"

            )

        ], className="logo-container"),


        html.Div([

            html.P(

                "Real-time air quality insights for cities across the United States",

                className="subtitle"

            )

        ], className="subtitle-container")

    ], className="dashboard-header"),


#====== Air Flow Decoration

    html.Div(

        [

            html.Img(

                src=app.get_asset_url("air-flow.svg"),

                className="air-flow-left"

            ),

            html.Img(

                src=app.get_asset_url("air-flow.svg"),

                className="air-flow-right"

            )

        ],

        className="air-flow-decoration"

    ),


#====== City and Date Selection

    html.Div([

        html.Div([

            html.Label("Select a city:"),

            dcc.Dropdown(

                id="city-dropdown",

                options=[

                    {

                        "label": city[1],

                        "value": city[0]

                    }

                    for city in cities

                ],

                placeholder="Choose a city"

            )

        ], style={"width": "55%"}),


        html.Div([

            html.Label("Select a date:"),

            dcc.DatePickerSingle(

                id="date-picker",

                placeholder="Select a date"

            )

        ], style={"width": "220px"})

    ], style={

        "display": "flex",

        "gap": "20px",

        "alignItems": "end",

        "backgroundColor": "#f8fafc",

        "padding": "20px",

        "borderRadius": "14px",

        "border": "1px solid #e5eaf0",

        "marginBottom": "20px"

    }),


#====== Error Message

    html.Div(

        id="error-message",

        style={

            "color": "red",

            "fontWeight": "bold",

            "textAlign": "center",

            "margin": "15px"

        }

    ),


#====== Overall AQI

    html.Div([

        html.P(

            "OVERALL AIR QUALITY",

            className="aqi-hero-label"

        ),

        html.Div(

            "--",

            id="overall-aqi"

        ),

        html.Div(

            "Select a city and date",

            id="aqi-status"

        ),

        html.P(

            "Based on the selected location and date",

            className="aqi-hero-description"

        )

    ], className="aqi-hero-card"),


#====== Average Pollutant Level

    html.H2("Daily Average Pollutant Levels"),


#====== Pollutant Cards

    html.Div([

        html.Div([

            html.H4("PM2.5"),

            html.Div(

                id="pm25-value",

                children="--"

            ),

            html.P("Fine particles")

        ], className="pollutant-card"),


        html.Div([

            html.H4("PM10"),

            html.Div(

                id="pm10-value",

                children="--"

            ),

            html.P("Coarse particles")

        ], className="pollutant-card"),


        html.Div([

            html.H4("O₃"),

            html.Div(

                id="o3-value",

                children="--"

            ),

            html.P("Ozone")

        ], className="pollutant-card"),


        html.Div([

            html.H4("NO₂"),

            html.Div(

                id="no2-value",

                children="--"

            ),

            html.P("Nitrogen dioxide")

        ], className="pollutant-card"),


        html.Div([

            html.H4("SO₂"),

            html.Div(

                id="so2-value",

                children="--"

            ),

            html.P("Sulfur dioxide")

        ], className="pollutant-card"),


        html.Div([

            html.H4("CO"),

            html.Div(

                id="co-value",

                children="--"

            ),

            html.P("Carbon monoxide")

        ], className="pollutant-card")

    ], className="pollutant-container"),


#====== Reference Tables

    html.H2("Air Quality Reference Guide"),


    html.Div([


#====== Left Table

        html.Div([

            html.H3("Daily Average Pollutant Levels"),

            dash_table.DataTable(

                id="daily-average-table",

                columns=[

                    {

                        "name": "Pollutant",

                        "id": "Pollutant"

                    },

                    {

                        "name": "Daily Average",

                        "id": "Daily Average"

                    }

                ],

                style_cell={

                    "textAlign": "center",

                    "padding": "5px",

                    "fontSize": "13px"

                },

                style_header={

                    "fontWeight": "bold",

                    "fontSize": "13px"

                }

            )

        ], style={"width": "35%"}),


#====== Right Table

        html.Div([

            html.H3("AQ Reference"),

            dash_table.DataTable(

                columns=[

                    {

                        "name": ["", "Qualitative name"],

                        "id": "quality"

                    },

                    {

                        "name": [

                            "Pollutant concentration in μg/m³",

                            "SO₂"

                        ],

                        "id": "so2"

                    },

                    {

                        "name": [

                            "Pollutant concentration in μg/m³",

                            "NO₂"

                        ],

                        "id": "no2"

                    },

                    {

                        "name": [

                            "Pollutant concentration in μg/m³",

                            "PM10"

                        ],

                        "id": "pm10"

                    },

                    {

                        "name": [

                            "Pollutant concentration in μg/m³",

                            "PM2.5"

                        ],

                        "id": "pm25"

                    },

                    {

                        "name": [

                            "Pollutant concentration in μg/m³",

                            "O₃"

                        ],

                        "id": "o3"

                    },

                    {

                        "name": [

                            "Pollutant concentration in μg/m³",

                            "CO"

                        ],

                        "id": "co"

                    }

                ],

                data=[

                    {

                        "quality": "Good",

                        "so2": "[0, 20)",

                        "no2": "[0, 40)",

                        "pm10": "[0, 20)",

                        "pm25": "[0, 10)",

                        "o3": "[0, 60)",

                        "co": "[0, 4400)"

                    },

                    {

                        "quality": "Fair",

                        "so2": "[20, 80)",

                        "no2": "[40, 70)",

                        "pm10": "[20, 50)",

                        "pm25": "[10, 25)",

                        "o3": "[60, 100)",

                        "co": "[4400, 9400)"

                    },

                    {

                        "quality": "Moderate",

                        "so2": "[80, 250)",

                        "no2": "[70, 150)",

                        "pm10": "[50, 100)",

                        "pm25": "[25, 50)",

                        "o3": "[100, 140)",

                        "co": "[9400, 12400)"

                    },

                    {

                        "quality": "Poor",

                        "so2": "[250, 350)",

                        "no2": "[150, 200)",

                        "pm10": "[100, 200)",

                        "pm25": "[50, 75)",

                        "o3": "[140, 180)",

                        "co": "[12400, 15400)"

                    },

                    {

                        "quality": "Very Poor",

                        "so2": "≥350",

                        "no2": "≥200",

                        "pm10": "≥200",

                        "pm25": "≥75",

                        "o3": "≥180",

                        "co": "≥15400"

                    }

                ],

                merge_duplicate_headers=True,

                style_cell={

                    "textAlign": "center",

                    "padding": "6px",

                    "fontSize": "11px",

                    "whiteSpace": "normal",

                    "height": "auto"

                },

                style_header={

                    "fontWeight": "bold",

                    "fontSize": "11px"

                }

            )

        ], style={"width": "60%"})

    ], style={

        "display": "flex",

        "gap": "15px",

        "alignItems": "flex-start",

        "width": "100%"

    }),


#====== Hourly AQI

    html.H2("Average AQI by Hour"),

    html.Div([

        dcc.Graph(

            id="aqi-hourly-graph",

            style={"height": "350px"}

        )

    ], style={

        "backgroundColor": "#ffffff",

        "borderRadius": "14px",

        "border": "1px solid #e5eaf0",

        "padding": "10px",

        "marginBottom": "25px"

    }),


#====== Best and Worst AQI

    html.Div([

        html.Div([

            html.H3("Worst AQI"),

            html.Div(

                id="worst-aqi",

                className="aqi-result"

            )

        ], className="aqi-card"),


        html.Div([

            html.H3("Best AQI"),

            html.Div(

                id="best-aqi",

                className="aqi-result"

            )

        ], className="aqi-card")

    ], className="aqi-cards-container"),


#====== AQI Distribution

    html.H2("AQI Distribution Across All Available Dates"),

    html.Div([

        dcc.Graph(

            id="aqi-pie-graph",

            style={"height": "400px"}

        )

    ], style={

        "backgroundColor": "#ffffff",

        "borderRadius": "14px",

        "border": "1px solid #e5eaf0",

        "padding": "10px",

        "marginBottom": "30px"

    }),


#====== AI Air Quality Chatbot

    html.H2("Ask Air Tracker AI"),

    html.P(

        "Ask questions about the selected city's air quality."

    ),


    dcc.Store(

        id="ai-chat-history",

        data=[]

    ),


    html.Div(

        [

            html.Div(

                [

                    html.Strong("Air Tracker AI"),

                    dcc.Markdown(

                        "Hi! I'm your Air Tracker assistant. "

                        "Ask me anything about the selected city's air quality."

                    )

                ],

                style={

                    "backgroundColor": "#ffffff",

                    "padding": "14px 17px",

                    "borderRadius": "16px",

                    "border": "1px solid #dfe7ed",

                    "maxWidth": "82%",

                    "marginBottom": "13px"

                }

            )

        ],

        id="ai-chat-history-display"

    ),


    html.Div(

        [

            dcc.Input(

                id="ai-question",

                type="text",

                placeholder="Ask about the air quality..."

            ),

            html.Button(

                "Ask",

                id="ai-button",

                n_clicks=0

            )

        ]

    )

])


#====== Dashboard Callback

@app.callback(

    Output("daily-average-table", "data"),

    Output("aqi-hourly-graph", "figure"),

    Output("overall-aqi", "children"),

    Output("aqi-status", "children"),

    Output("pm25-value", "children"),

    Output("pm10-value", "children"),

    Output("o3-value", "children"),

    Output("no2-value", "children"),

    Output("so2-value", "children"),

    Output("co-value", "children"),

    Output("worst-aqi", "children"),

    Output("best-aqi", "children"),

    Output("aqi-pie-graph", "figure"),

    Output("error-message", "children"),

    Input("city-dropdown", "value"),

    Input("date-picker", "date")

)


def update_dashboard(city_id, selected_date):


#====== Error if no city or date selected

    if city_id is None or selected_date is None:

        return (

            [],

            {},

            "--",

            "Select a city and date",

            "--",

            "--",

            "--",

            "--",

            "--",

            "--",

            "",

            "",

            {},

            "Please select a city and a date."

        )


#====== Extract Pollutant Information

    conn = get_connection()

    with conn.cursor() as cursor:

        cursor.execute("""

            SELECT

                reading_time_utc,

                carbon_monoxide,

                nitric_oxide,

                nitrogen_dioxide,

                ozone,

                sulfur_dioxide,

                fine_particles,

                coarse_particles,

                ammonia,

                aqi

            FROM air_pollution_table

            WHERE city_id = %s

                AND reading_time_utc::date = %s

            ORDER BY reading_time_utc;

        """, (city_id, selected_date))

        rows = cursor.fetchall()


#====== Extract Best and Worst AQI

    with conn.cursor() as cursor:

        cursor.execute("""

            SELECT aqi, reading_time_utc

            FROM air_pollution_table

            WHERE city_id = %s

                AND aqi IS NOT NULL

                AND aqi <> 0

            ORDER BY aqi ASC, reading_time_utc ASC

            LIMIT 1;

        """ , (city_id,))

        best_result = cursor.fetchone()


        cursor.execute("""

            SELECT aqi, reading_time_utc

            FROM air_pollution_table

            WHERE city_id = %s

                AND aqi IS NOT NULL

                AND aqi <> 0

            ORDER BY aqi DESC, reading_time_utc ASC

            LIMIT 1;

        """, (city_id,))

        worst_result = cursor.fetchone()


#====== Extract Information for Pie Graph

    with conn.cursor() as cursor:

        cursor.execute("""

            SELECT

                aqi,

                COUNT(*)

            FROM air_pollution_table

            WHERE city_id = %s

                AND aqi IS NOT NULL

            GROUP BY aqi

            ORDER BY aqi;

        """, (city_id,))

        aqi_counts = cursor.fetchall()


    conn.close()


#====== Create DataFrame

    df = pd.DataFrame(

        rows,

        columns=[

            "reading_time_utc",

            "carbon_monoxide",

            "nitric_oxide",

            "nitrogen_dioxide",

            "ozone",

            "sulfur_dioxide",

            "fine_particles",

            "coarse_particles",

            "ammonia",

            "aqi"

        ]

    )


#====== Error if data is not available

    if df.empty:

        return (

            [],

            {},

            "--",

            "No data",

            "--",

            "--",

            "--",

            "--",

            "--",

            "--",

            "No data",

            "No data",

            {},

            "No data is available for this city and date."

        )


#====== Dropping NA's

    df = df.dropna(subset=["aqi"])


#====== Changing the Displayed Pollutant Names

    pollutants = [

        "carbon_monoxide",

        "nitrogen_dioxide",

        "ozone",

        "sulfur_dioxide",

        "fine_particles",

        "coarse_particles"

    ]


    pollutant_names = {

        "carbon_monoxide": "CO",

        "nitrogen_dioxide": "NO₂",

        "ozone": "O₃",

        "sulfur_dioxide": "SO₂",

        "fine_particles": "PM2.5",

        "coarse_particles": "PM10"

    }


#====== Updating the Table with Mean Values

    daily_average = df[pollutants].mean().round(2)


    table_data = [

        {

            "Pollutant": pollutant_names[pollutant],

            "Daily Average": value

        }

        for pollutant, value in daily_average.items()

    ]


#====== Overall AQI

    overall_aqi = round(

        df["aqi"].mean(),

        2

    )


    if overall_aqi <= 1:

        aqi_status = "Very Good"

    elif overall_aqi <= 2:

        aqi_status = "Good"

    elif overall_aqi <= 3:

        aqi_status = "Moderate"

    elif overall_aqi <= 4:

        aqi_status = "Poor"

    else:

        aqi_status = "Very Poor"


#====== Converting Times

    df["reading_time_utc"] = pd.to_datetime(

        df["reading_time_utc"]

    )


    df["hour"] = df["reading_time_utc"].dt.hour


#====== Error if there's unexpected number of observations

    observation_count = (

        df["reading_time_utc"].dt.hour.nunique()

    )


    if observation_count != 24:

        return (

            table_data,

            {},

            overall_aqi,

            aqi_status,

            daily_average["fine_particles"],

            daily_average["coarse_particles"],

            daily_average["ozone"],

            daily_average["nitrogen_dioxide"],

            daily_average["sulfur_dioxide"],

            daily_average["carbon_monoxide"],

            "",

            "",

            {},

            f"Incomplete data: only {observation_count} of 24 hourly observations are available."

        )


#====== Hourly AQI

    hourly_aqi = (

        df.groupby(

            "hour",

            as_index=False

        )["aqi"].mean()

    )


#====== AQI Distribution Data

    aqi_count_df = pd.DataFrame(

        aqi_counts,

        columns=[

            "aqi",

            "count"

        ]

    )


    aqi_names = {

        1: "1 - Good",

        2: "2 - Fair",

        3: "3 - Moderate",

        4: "4 - Poor",

        5: "5 - Very Poor"

    }


    aqi_count_df["category"] = (

        aqi_count_df["aqi"].map(aqi_names)

    )


#====== Hourly AQI Graph

    aqi_graph = px.line(

        hourly_aqi,

        x="hour",

        y="aqi",

        markers=True

    )


    aqi_graph.update_traces(

        line_width=3,

        marker_size=8

    )


    aqi_graph.update_layout(

        title="Hourly Air Quality",

        xaxis_title="Hour of Day",

        yaxis_title="Air Quality",

        template="plotly_white",

        paper_bgcolor="white",

        plot_bgcolor="white",

        margin={

            "l": 80,

            "r": 30,

            "t": 55,

            "b": 55

        },

        hovermode="x unified"

    )


    aqi_graph.update_xaxes(

        range=[0, 23],

        dtick=2,

        showgrid=True,

        gridcolor="#e8edf2"

    )


    aqi_graph.update_yaxes(

        range=[0.8, 5.2],

        tickvals=[1, 2, 3, 4, 5],

        ticktext=[

            "1 - Good",

            "2 - Fair",

            "3 - Moderate",

            "4 - Poor",

            "5 - Very Poor"

        ],

        showgrid=True,

        gridcolor="#e8edf2"

    )


#====== Best and Worst AQI

    if best_result is not None:

        best_aqi, best_date = best_result

        best_aqi_text = (

            f"{best_aqi} \n| "

            f"Date:\n\n{best_date.strftime('%Y-%m-%d %I:%M %p')}"

        )

    else:

        best_aqi_text = "No best AQI data available."


    if worst_result is not None:

        worst_aqi, worst_date = worst_result

        worst_aqi_text = (

            f"{worst_aqi} \n| "

            f"Date: \n\n{worst_date.strftime('%Y-%m-%d %I:%M %p')}"

        )

    else:

        worst_aqi_text = "No worst AQI data available."


#====== AQI Distribution

    aqi_pie_graph = px.pie(

        aqi_count_df,

        names="category",

        values="count"

    )


    aqi_pie_graph.update_traces(

        textinfo="percent+label",

        hovertemplate=(

            "AQI: %{label}<br>"

            "Observations: %{value}"

            "<extra></extra>"

        )

    )


    aqi_pie_graph.update_layout(

        title="AQI Distribution",

        template="plotly_white",

        paper_bgcolor="white",

        plot_bgcolor="white",

        margin={

            "l": 20,

            "r": 20,

            "t": 55,

            "b": 20

        }

    )


#====== Return Callback Outputs

    return (

        table_data,

        aqi_graph,

        overall_aqi,

        aqi_status,

        daily_average["fine_particles"],

        daily_average["coarse_particles"],

        daily_average["ozone"],

        daily_average["nitrogen_dioxide"],

        daily_average["sulfur_dioxide"],

        daily_average["carbon_monoxide"],

        worst_aqi_text,

        best_aqi_text,

        aqi_pie_graph,

        ""

    )


#====== AI Chatbot Callback

@app.callback(

    Output("ai-chat-history-display", "children"),

    Output("ai-chat-history", "data"),

    Output("ai-question", "value"),

    Input("ai-button", "n_clicks"),

    State("ai-question", "value"),

    State("city-dropdown", "value"),

    State("date-picker", "date"),

    State("ai-chat-history", "data")

)


def update_ai_chat(

    n_clicks,

    question,

    city_id,

    selected_date,

    chat_history

):


#====== Check Chat History

    if chat_history is None:

        chat_history = []


#====== Welcome Message

    if not n_clicks:

        return [

            html.Div(

                [

                    html.Strong(

                        "Air Tracker AI",

                        style={

                            "fontSize": "14px"

                        }

                    ),

                    dcc.Markdown(

                        "Hi! I'm your Air Tracker assistant. "

                        "Ask me anything about the selected city's air quality.",

                        style={

                            "margin": "5px 0 0 0"

                        }

                    )

                ],

                style={

                    "backgroundColor": "#ffffff",

                    "padding": "14px 17px",

                    "borderRadius": "16px",

                    "border": "1px solid #dfe7ed",

                    "maxWidth": "82%",

                    "marginBottom": "13px"

                }

            )

        ], chat_history, ""


#====== Check for Empty Question

    if not question or not question.strip():

        return [], chat_history, ""


#====== Check City and Date

    if city_id is None or selected_date is None:

        return [

            html.Div(

                "Please select a city and date before asking Air Tracker AI a question.",

                style={

                    "color": "#c0392b",

                    "padding": "10px"

                }

            )

        ], chat_history, ""


#====== Get City Name

    city_name = next(

        city[1]

        for city in cities

        if city[0] == city_id

    )


#====== Get Air Quality Data

    conn = get_connection()

    cur = conn.cursor()


    cur.execute(

        """

        SELECT

            carbon_monoxide,

            nitrogen_dioxide,

            ozone,

            sulfur_dioxide,

            fine_particles,

            coarse_particles,

            aqi

        FROM air_pollution_table

        WHERE city_id = %s

          AND reading_time_utc::date = %s

        ORDER BY reading_time_utc;

        """,

        (city_id, selected_date)

    )


    readings = cur.fetchall()


    cur.close()

    conn.close()


#====== Check for Data

    if not readings:

        return [

            html.Div(

                "There is no air quality data available for this city and date.",

                style={

                    "color": "#c0392b"

                }

            )

        ], chat_history, ""


#====== Calculate Air Quality Information

    data = pd.DataFrame(

        readings,

        columns=[

            "carbon_monoxide",

            "nitrogen_dioxide",

            "ozone",

            "sulfur_dioxide",

            "fine_particles",

            "coarse_particles",

            "aqi"

        ]

    )


    daily_average = data[

        [

            "carbon_monoxide",

            "nitrogen_dioxide",

            "ozone",

            "sulfur_dioxide",

            "fine_particles",

            "coarse_particles"

        ]

    ].mean().round(2)


    overall_aqi = round(

        data["aqi"].mean(),

        2

    )


#====== Previous Conversation

    conversation = ""


    for message in chat_history:

        conversation += (

            f'{message["role"]}: '

            f'{message["message"]}\n'

        )


#====== AI Prompt

    prompt = f"""

You are Air Tracker AI, a conversational assistant for the City Air Tracker dashboard.

Your job is to help users understand air quality data and use that information at their own discretion.

City: {city_name}

Date: {selected_date}

Overall AQI: {overall_aqi}

Pollutant averages:

PM2.5: {daily_average["fine_particles"]}

PM10: {daily_average["coarse_particles"]}

O3: {daily_average["ozone"]}

NO2: {daily_average["nitrogen_dioxide"]}

SO2: {daily_average["sulfur_dioxide"]}

CO: {daily_average["carbon_monoxide"]}

Previous conversation:

{conversation}

User question:

{question}

Answer the user's question using the air quality data above.

Be conversational and helpful.

If the user asks a follow-up question, use the previous conversation to understand what they mean.

Do not make up air quality measurements that are not provided.

If you don't know, simply say you don't know.

Do not use LaTeX or mathematical notation.

Use normal names such as O3, NO2, SO2, PM2.5, PM10, and CO.

Use simple Markdown when helpful.

For health-related questions, provide general information only.

Do not diagnose medical conditions or claim to provide medical advice.

If the available data is not enough to answer the question, clearly say that.

If the user asks a question that is inappropriate, redirect them to the questions you can answer.

If they keep insisting, end the conversation.

"""


#====== Get AI Response

    ai_response = get_ai(prompt)


#====== Save Conversation

    chat_history.append(

        {

            "role": "user",

            "message": question

        }

    )


    chat_history.append(

        {

            "role": "assistant",

            "message": ai_response

        }

    )


#====== Display Conversation

    chat_display = []


    for message in chat_history:

        if message["role"] == "user":

            chat_display.append(

                html.Div(

                    [

                        html.Strong(

                            "You",

                            style={

                                "fontSize": "14px"

                            }

                        ),

                        dcc.Markdown(

                            message["message"],

                            style={

                                "margin": "5px 0 0 0"

                            }

                        )

                    ],

                    style={

                        "backgroundColor": "#f4f7fb",

                        "padding": "12px",

                        "borderRadius": "10px",

                        "marginBottom": "10px"

                    }

                )

            )

        else:

            chat_display.append(

                html.Div(

                    [

                        html.Strong(

                            "Air Tracker AI",

                            style={

                                "fontSize": "14px"

                            }

                        ),

                        dcc.Markdown(

                            message["message"],

                            style={

                                "margin": "5px 0 0 0"

                            }

                        )

                    ],

                    style={

                        "backgroundColor": "#ffffff",

                        "padding": "12px",

                        "borderRadius": "10px",

                        "marginBottom": "10px",

                        "border": "1px solid #e5eaf0"

                    }

                )

            )


    return chat_display, chat_history, ""


#====== Run App

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(os.getenv("PORT", 8050)),

        debug=False

    )