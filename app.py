
# このウェブアプリは、Streamlitフレームワークを使用して構築されています。
# GeoNet APIから最新の地震データを取得し、そのデータをGoogle Gemini APIに渡して
# 専門家向けまたは一般向けのレポートを自動生成します。
#
# 主要な機能:
# 1. GeoNet APIからリアルタイム地震データを取得し、データをキャッシュする。
# 2. 地震データを地図上にプロットし、インタラクティブなチャートで可視化する。
# 3. ユーザーのペルソナ（例: 不動産業者）に基づいて、LLMにレポートを作成させる。
# 4. LLMから返された構造化されたJSONデータを美しく整形して表示する。
#

import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd
import altair as alt
import time
import os

#---------------------------------------------------------------------------------------------------
# 1. APIキーの設定とAPI呼び出し関数
#---------------------------------------------------------------------------------------------------



@st.cache_data(ttl=30)
def get_latest_earthquakes():
    """
    GeoNet APIから最新の地震データを取得する関数。
    データは30秒間キャッシュされます。
    MMI=3のパラメータは、人が揺れを感じ始める最低レベルを表します。
    """
    api_url = "https://api.geonet.org.nz/quake?MMI=3"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        
        earthquake_data = response.json()
        formatted_data = []
        
        # 最新の地震を上位5件に限定
        for feature in earthquake_data['features'][:5]:
            props = feature['properties']
            
            # タイムスタンプを読みやすい形式に変換
            time_utc = datetime.fromisoformat(props['time'].replace('Z', '+00:00'))
            
            formatted_data.append({
                "ID": props['publicID'],
                "Location": props['locality'],
                "Magnitude": props['magnitude'],
                "Depth (km)": props['depth'],
                "Shaking Intensity (MMI)": props['mmi'],
                "Time (NZST)": time_utc.strftime('%Y-%m-%d %H:%M:%S'),
                "latitude": feature['geometry']['coordinates'][1],
                "longitude": feature['geometry']['coordinates'][0]
            })
            
        return formatted_data
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error accessing the GeoNet API: {e}")
        return None

def call_llm_api(prompt):
    """
    Calls a local Ollama model to generate a response in a structured JSON format.
    Assumes Ollama is running at http://localhost:11434.
    """
    url = "http://172.24.48.191:11434/api/generate"
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


#---------------------------------------------------------------------------------------------------
# 2. Streamlit UIの構築
#---------------------------------------------------------------------------------------------------

NOTIFICATION_FILE = "notification_status.txt"

def read_notification_status():
    """
    通知ファイルからメッセージを読み込む関数。
    """
    if os.path.exists(NOTIFICATION_FILE):
        with open(NOTIFICATION_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content:
            return content
    return None

# サイドバーをUIの整理に使用
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
st.markdown("This app provides a clear report on the latest GeoNet data, which is **automatically refreshed every 30 seconds**.")

# Read and display notifications from the background scheduler
notification_message = read_notification_status()
if notification_message:
    st.error(notification_message) # Use st.error for major quake alerts

# アプリは、インタラクションまたはリフレッシュごとに上から下に実行される
st.info(f"Fetching information... (Automatically updates every 30 seconds, last updated: {datetime.now().strftime('%H:%M:%S')})")
quakes = get_latest_earthquakes()

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
    
    prompt = f"""
    You are a friendly reporter specializing in New Zealand earthquake information.
    Based on the latest earthquake data below, please provide a concise and calm explanation
    of the potential impacts in a way that is easy for the general public to understand.
    Avoid using technical jargon.
    
    User's request: '{user_persona}'
    
    ---
    Latest Earthquake Data:
    {json.dumps(quakes, indent=2, ensure_ascii=False)}
    ---
    
    Focus the response on the earthquake's location, magnitude, and potential impacts.
    
    Please provide the response in a JSON format with the following keys:
    - 'report_title': A title for the report.
    - 'summary': A brief summary of the earthquake situation.
    - 'impacts': An array of objects, where each object describes a specific earthquake's location, magnitude, and potential impact.
    """
    
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

# ページを手動でリフレッシュするためのボタンを追加
if st.button("Refresh data"):
    st.rerun()
