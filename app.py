import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd
import altair as alt
import time
import os
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh
from pyproj import Transformer
# Load environment variables from .env file
load_dotenv()

#---------------------------------------------------------------------------------------------------
# 1. Setting the API key and API call function
#---------------------------------------------------------------------------------------------------

@st.cache_data(ttl=300)# Cache for 5 minutes instead of 30 seconds
def fetch_latest_earthquakes():
    """
    Fetch latest earthquake data from GeoNet API.
    Data is cached for 5 minutes to reduce API load.
    """
    api_url = "https://api.geonet.org.nz/quake?MMI=3"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        earthquakes = []
        for feature in data['features'][:5]:
            props = feature['properties']
            time_utc = datetime.fromisoformat(props['time'].replace('Z', '+00:00'))
            
            earthquakes.append({
                "ID": props['publicID'],
                "Location": props['locality'],
                "Magnitude": props['magnitude'],
                "Depth (km)": props['depth'],
                "Shaking Intensity (MMI)": props['mmi'],
                "Time (NZST)": time_utc.strftime('%Y-%m-%d %H:%M:%S'),
                "latitude": feature['geometry']['coordinates'][1],
                "longitude": feature['geometry']['coordinates'][0]
            })
        return earthquakes
    except requests.exceptions.RequestException as e:
        st.error(f"Error accessing GeoNet API: {e}")
        return None

def call_llm_api(prompt):
    """
    Calls a local Ollama model to generate a response in a structured JSON format.
    Assumes Ollama is running at http://localhost:11434.
    """
    url = "http://127.0.0.1:11434/api/generate"
    headers = {
        "Content-Type": "application/json",
    }
    
    # Define the model to use. Make sure you have this model pulled in Ollama.
    # You can change "llama3" to any other model you have available.
    model_name = "llama3"

    # The prompt already asks for a JSON output, which is good.
    # Ollama's `generate` endpoint expects a `prompt` field.
    # The `format: "json"` parameter helps ensure the output is valid JSON.
    payload = {
        "model": model_name,
        "prompt": prompt,
        "format": "json", # Request JSON output from Ollama
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        # Ollama (with format: "json") returns a JSON object where the 'response' field contains the JSON string.
        ollama_response = response.json()
        json_string = ollama_response.get('response')

        if json_string:
            try:
                # The response itself is a JSON string, so we parse it again.
                llm_data = json.loads(json_string)
                return llm_data
            except json.JSONDecodeError:
                return {"error": "Failed to parse the JSON content from the LLM response."}
        else:
            return {"error": "The API returned an empty or malformed response."}

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Ollama API: {e}. Is Ollama running?")
        return {"error": "Could not connect to the local LLM server."}
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred while calling the LLM."}

def get_population_data_from_statsnz(longitude, latitude, radius_meters=10000):
    """
    A function that retrieves population-related data around specified coordinates from the Stats NZ Spatial Query API.
    """
    api_key = os.getenv("STATS_NZ_API_KEY")
    if not api_key:
        st.warning("STATS_NZ_API_KEY not found in .env file. Population data will not be fetched.")
        return None

    # Layer ID 115044 is assumed to be a population-related boundary layer based on previous search.
    # We need to confirm its exact nature for proper interpretation.
    layer_id = "115044" 
    
    # Stats NZ API expects coordinates in NZTM2000 projection (EPSG:2193)
    # However, the API example uses x and y which typically correspond to longitude and latitude in WGS84 (EPSG:4326)
    # For simplicity, we'll assume the API can handle WGS84 for now, or requires a transformation.
    # If the API truly requires NZTM2000, a coordinate transformation step would be needed here.
    
    api_url = (f"https://datafinder.stats.govt.nz/services/query/v1/vector.json?"
               f"key={api_key}&layer={layer_id}&x={longitude}&y={latitude}&"
               f"max_results=10&radius={radius_meters}&geometry=true&with_field_names=true")
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        if data and 'features' in data:
            # Extract relevant properties from features
            # The exact fields will depend on the layer's schema
            population_info = []
            for feature in data['features']:
                props = feature.get('properties', {})
                # Assuming 'name' and 'population' or similar fields exist
                # This part needs adjustment once we know the exact schema of layer 115044
                population_info.append({
                    "Name": props.get('name', 'N/A'),
                    "Value": props.get('value', 'N/A'), # Placeholder, actual field name needed
                    "Geometry": feature.get('geometry')
                })
            return population_info
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error accessing Stats NZ API: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching population data: {e}")
        return None


#---------------------------------------------------------------------------------------------------
# 2. Building the Streamlit UI
#---------------------------------------------------------------------------------------------------

NOTIFICATION_FILE = "notification_status.txt"

def read_notification_status():
    """
    A function to read messages from the notification file.
    """
    if os.path.exists(NOTIFICATION_FILE):
        with open(NOTIFICATION_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content:
            return content
    return None

# Use the sidebar to organize your UI
with st.sidebar:
    st.header("App Settings")
    user_persona = st.text_input("Report for:", placeholder="e.g., 'real estate agent' or 'urban planner'")
    st.markdown("---")
    st.header("Project Innovation")
    st.markdown("""
    - **Technical Interest**: Combines **Natural Language (LLM)** & **Geospatial Data (GIS)**.
    - **Interactive Demo**: Dynamic map & customizable reports.
    - **Clear Use Cases**: Adaptable for **real estate agents** & **urban planners**.
    """)
    st.markdown("---")
    st.header("Further Improvements (Concept)")
    st.markdown("- **Notification Feature**: Background alerts for major quakes.")
    st.markdown("- **Historical Data**: Could be expanded to include historical quake analysis.")

st.title("GeoNet Real-time Earthquake Reporter 🌏")
st.markdown("This app provides a clear report on the latest GeoNet data, which is **automatically refreshed every 5 minutes**.")

# Read and display notifications from the background scheduler
notification_message = read_notification_status()
if notification_message:
    st.error(notification_message) # Use st.error for major quake alerts

# The app runs from top to bottom with each interaction or refresh.
st.info(f"Fetching information... (Automatically updates every 5 minutes, last updated: {datetime.now().strftime('%H:%M:%S')})")
quakes = fetch_latest_earthquakes()

def log_earthquake_data(quakes):
    """
    A function to append and save earthquake data to a CSV file.
    """
    if not quakes:
        return

    os.makedirs("data", exist_ok=True)
    log_path = "data/earthquake_log.csv"

    df = pd.DataFrame(quakes)
    df["logged_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    df.to_csv(log_path, mode='a', index=False, header=not os.path.exists(log_path))

if quakes:

    if quakes and quakes[0]['Magnitude'] is not None:
        st.subheader("📍 Recent Earthquakes on the Map")
        
        earthquake_df = pd.DataFrame(quakes)
        st.map(earthquake_df, latitude='latitude', longitude='longitude', zoom=4)
        
        st.subheader("📊 Earthquake Magnitude Distribution")
        chart = alt.Chart(earthquake_df).mark_bar().encode(
            x=alt.X('Magnitude:Q', bin=True),
            y='count()',
            tooltip=['Magnitude', 'count()']
        ).properties(
            title='Frequency of Earthquakes by Magnitude'
        )
        st.altair_chart(chart, use_container_width=True)
        
        st.subheader("📝 Latest Earthquake Data")
        st.write(earthquake_df)

        # Fetch and display population data for the latest earthquake
        latest_quake = quakes[0]
        st.subheader(f"👥 Population Data near {latest_quake['Location']}")
        
        # Assuming longitude and latitude are available in latest_quake
        population_data = get_population_data_from_statsnz(
            latest_quake['longitude'], 
            latest_quake['latitude']
        )
        
        if population_data:
            # For now, just display the raw data.
            # Later, this can be processed into a GeoDataFrame and visualized.
            st.json(population_data) 
        else:
            st.info("No population data found or API key missing for this location.")
        
        with open("llm_prompt.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        
        prompt = prompt_template.replace("{{earthquake_data}}", json.dumps(quakes, indent=2, ensure_ascii=False)) \
                            .replace("{{population_data}}", json.dumps(population_data, indent=2, ensure_ascii=False))
            
        llm_response = call_llm_api(prompt)
        
        st.subheader("🤖 LLM Report")
        
        if 'error' in llm_response:
            st.error(llm_response['error'])
        else:
            st.write(f"### {llm_response.get('report_title', 'Report')}")
            st.write(llm_response.get('summary', ''))
            
            if 'impacts' in llm_response:
                impacts_df = pd.DataFrame(llm_response['impacts'])
                st.table(impacts_df)
    else:
        st.warning("Could not fetch earthquake data. Please try again later.")

# Add a manual refresh button
# if st.button("Refresh data"):
#     st.rerun()

st_autorefresh(interval=300000, limit=100, key="auto_refresh")