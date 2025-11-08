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

### 4. Run the Application

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

## Implemented Improvements

*   **Notification Feature (Alert System)**:
    *   Uses `apscheduler` to monitor the GeoNet API in the background.
    *   Detects earthquakes with Magnitude 4.0 or higher and writes messages to `notification_status.txt`.
    *   The Streamlit app reads `notification_status.txt` and displays alerts in the UI.

## Future Improvement Ideas (Phase 2 onwards)

1.  **Enhanced Notification System**: Implement real-time email/SMS alerts (e.g., using SendGrid/Twilio).
2.  **Historical Data Analysis**: Utilize GeoNet's historical data API or CSV data for long-term earthquake trend analysis and visualization.
3.  **Urban Impact Map**: Overlay GIS layers (population density, building distribution, ground conditions) to visualize vulnerable areas and high-risk cities as heatmaps.
4.  **Real-time LLM Enhancement**: Refine LLM prompts to automatically generate more detailed insights, such as "which cities are most affected" and "recommended countermeasures."
5.  **User-Specific Reports**: Adjust LLM output tone (prompt tuning) based on user roles (e.g., urban planners, real estate agents, disaster management personnel).
