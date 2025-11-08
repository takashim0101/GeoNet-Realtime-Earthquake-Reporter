import requests
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time

# Define the path for the notification status file
NOTIFICATION_FILE = "notification_status.txt"
MAGNITUDE_THRESHOLD = 4.0

def get_latest_earthquakes_background():
    """
    GeoNet APIから最新の地震データを取得する関数 (バックグラウンド用)。
    Streamlitのキャッシュは使用せず、純粋なデータ取得を行います。
    """
    api_url = "https://api.geonet.org.nz/quake?MMI=3"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        
        earthquake_data = response.json()
        formatted_data = []
        
        for feature in earthquake_data['features'][:5]: # Limit to top 5 for efficiency
            props = feature['properties']
            
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
        print(f"Error accessing the GeoNet API in background: {e}")
        return None

def check_for_major_quakes():
    """
    主要な地震をチェックし、通知ファイルに書き込む関数。
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for major earthquakes...")
    quakes = get_latest_earthquakes_background()
    
    if quakes:
        major_quake_detected = False
        notification_messages = []
        for quake in quakes:
            if quake['Magnitude'] is not None and quake['Magnitude'] >= MAGNITUDE_THRESHOLD:
                major_quake_detected = True
                message = (
                           f"🚨 Major Earthquake Detected! "
                           f"Magnitude: {quake['Magnitude']}, "
                           f"Location: {quake['Location']}, "
                           f"Time: {quake['Time (NZST)']}")
                notification_messages.append(message)
        
        if major_quake_detected:
            with open(NOTIFICATION_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(notification_messages))
            print(f"Major quake notification written to {NOTIFICATION_FILE}")
        else:
            # Clear the notification file if no major quakes are detected
            if os.path.exists(NOTIFICATION_FILE):
                os.remove(NOTIFICATION_FILE)
                print(f"No major quakes, {NOTIFICATION_FILE} cleared.")
    else:
        print("No earthquake data received from GeoNet API.")
        # Also clear the file if there's an API error
        if os.path.exists(NOTIFICATION_FILE):
            os.remove(NOTIFICATION_FILE)
            print(f"API error, {NOTIFICATION_FILE} cleared.")

if __name__ == "__main__":
    # Ensure the notification file exists and is empty on startup
    if os.path.exists(NOTIFICATION_FILE):
        os.remove(NOTIFICATION_FILE)
    
    scheduler = BackgroundScheduler()
    # Schedule check_for_major_quakes to run every 30 seconds
    scheduler.add_job(check_for_major_quakes, 'interval', seconds=30)
    
    print("Starting notification scheduler. Press Ctrl+C to exit.")
    scheduler.start()

    try:
        # This is to keep the main thread alive so that the scheduler can run
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler shut down.")
