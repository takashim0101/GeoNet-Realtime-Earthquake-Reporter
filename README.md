# GeoNet Real-time Earthquake Reporter

## Project Overview

This project is a Streamlit application that retrieves real-time earthquake data from the GeoNet API in New Zealand, visualizes it, and then uses an LLM (Large Language Model) to automatically generate expert-level reports. The primary goal is to quickly assess the impact of earthquakes from an urban planning and disaster prevention perspective.

## Feature Highlights

*   **Real-time Data Integration**: Automatically updates with the latest earthquake data from the GeoNet API every 30 seconds.
*   **Map + Graph + Report Integration**:
    *   Visualizes the latest earthquakes on an interactive map.
    *   Instantly grasps earthquake trends with a magnitude distribution graph.
    *   An LLM (e.g., Ollama Llama3) generates natural language earthquake reports.
*   **Urban Planning Perspective**: Reports focus on the impact on infrastructure and urban development, providing practical information from the viewpoint of urban disaster prevention and land use.
*   **Background Notification System**: Detects major earthquakes (Magnitude 4.0 or higher) in the background, generates notifications, and displays them in the Streamlit app.

## Setup Instructions

### 1. Clone the Repository

First, clone this repository to your local machine.

```bash
git clone [Your GitHub Repository URL]
cd GeoNetRealtimelandslideeporter
```

### 2. Set Up Virtual Environment

Create a Python virtual environment and install the necessary libraries.

```bash
python -m venv venv
# For Windows
.\venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Up Ollama LLM

To run the LLM locally, install Ollama and download the `llama3` model.

*   Install Ollama: [https://ollama.com/](https://ollama.com/)
*   Download the `llama3` model:
    ```bash
    ollama run llama3
    ```
    (This will download the model and start the Ollama server.)

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of your project and add your Stats NZ API key:

```
STATS_NZ_API_KEY="YOUR_STATS_NZ_API_KEY"
```

Replace `"YOUR_STATS_NZ_API_KEY"` with your actual API key. This key is used to access population data.

### 5. Run the Application

The application consists of two parts:

#### a. Start the Notification Scheduler (Run in a separate terminal)

This monitors for major earthquakes in the background and generates notifications.

```bash
python notification_scheduler.py
```

#### b. Start the Streamlit App (Run in another separate terminal)

This launches the main web application.

```bash
streamlit run app.py
```

Access the URL displayed in your browser.

## Deployment

To deploy this app on Streamlit Community Cloud, you need to push your code to a GitHub repository.

1.  **Create a GitHub Repository**: Create a new repository on GitHub.
2.  **Link Local to Remote**:
    ```bash
    git remote add origin [Your GitHub Repository URL]
    git branch -M main
    git push -u origin main
    ```
3.  **Deploy from Streamlit Community Cloud**: From the Streamlit Community Cloud dashboard, select your GitHub repository to deploy.

**Note on Cloud Deployment Limitations**:
When deployed to Streamlit Community Cloud, the background notification system and the local Ollama LLM integration will not function as they do on your local machine. These parts would require re-architecting for a cloud deployment (e.g., using cloud-based LLM APIs, or separate cloud services for scheduling).

## Implemented Improvements

*   **Notification Feature (Alert System)**:
    *   `apscheduler` を使用してバックグラウンドでGeoNet APIを監視。
    *   M4.0以上の地震を検知した場合、`notification_status.txt` にメッセージを書き込み。
    *   Streamlitアプリは `notification_status.txt` を読み込み、UIにアラートを表示。
*   **Urban Impact Map - Population Data Integration (Initial)**:
    *   Integrated Stats NZ Spatial Query API to fetch population-related data around earthquake epicenters.
    *   Uses `STATS_NZ_API_KEY` loaded from `.env` for API access.
    *   The Streamlit app now displays raw JSON output of population data for the latest earthquake's location.

## Future Improvement Ideas (Phase 2 onwards)

1.  **Enhanced Notification System**: Implement real-time email/SMS alerts (e.g., using SendGrid/Twilio) or free alternatives like Discord/Slack webhooks.
2.  **Historical Earthquake Data Acquisition**: Programmatically fetch historical earthquake data from GeoNet (e.g., using the `/quake?MMI=(int)` endpoint for the last 365 days) for ML model training.
3.  **Urban Impact Map - Full ML/DL Integration**:
    *   **GIS Layers Acquisition**: Acquire building outlines (LINZ Data Service) and ground conditions (GNS Science geological maps/fault lines) (initially via manual download).
    *   **Feature Engineering**: Prepare historical earthquake data and GIS layers for ML models.
    *   **Model Selection & Training**: Develop and train ML/DL models for vulnerability assessment or damage prediction.
    *   **GIS Visualization**: Visualize predicted impact (e.g., heatmaps, risk scores) on the map using processed GIS data.
4.  **Real-time LLM Enhancement**: Refine LLM prompts to automatically generate more detailed insights, such as "which cities are most affected" and "recommended countermeasures."
5.  **User-Specific Reports**: Adjust LLM output tone (prompt tuning) based on user roles (e.g., urban planners, real estate agents, disaster management personnel).