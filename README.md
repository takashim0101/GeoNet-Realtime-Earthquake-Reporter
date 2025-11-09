# GeoNet Real-time Earthquake Reporter 🌏

## Project Overview

This Streamlit application retrieves real-time earthquake data from the GeoNet API in New Zealand, visualizes it, and uses a local LLM (e.g., Ollama Llama3) to generate expert-level impact reports.  
It is designed for urban planning, disaster prevention, and public sector communication.
This project reflects a reproducible GeoAI architecture designed for public-sector and educational deployment, emphasizing trust, transparency, and audience-aware messaging.

---

## 🔧 Features

- **Real-time Earthquake Monitoring**: Updates every 5 minutes using GeoNet API.
- **Interactive Visualization**:
  - Map of recent earthquakes
  - Magnitude distribution chart
- **LLM-Generated Reports**:
  - Natural language summaries based on seismic and population data
  - Tone tailored for public sector and educational audiences
- **Population-Aware Messaging**:
  - Integrates Stats NZ Spatial Query API
  - Adjusts impact messaging based on nearby population density
- **Background Notification System**:
  - Detects M4.0+ earthquakes
  - Displays alerts in the Streamlit UI

---


## 🧠 Prompt Design

The LLM prompt is stored in `.llm_prompt.txt`, guiding the model to produce clear, population-aware summaries.  
This design ensures:

- ✅ Reproducibility across environments
- ✅ Customization for different audiences (e.g., planners, educators)
- ✅ Trust and transparency for public sector use

**Prompt placeholders:**

- `{{earthquake_data}}` → Injects latest GeoNet data  
- `{{population_data}}` → Injects Stats NZ population context

---

## 🏛️ Public Sector & Educational Use

This app is ideal for:

- **LINZ**: Land use and infrastructure vulnerability
- **SCION / NIWA**: Environmental risk communication
- **Educators**: Teaching geospatial reasoning and disaster preparedness
- **Local Councils**: Public messaging and community awareness

---

## Setup Instructions

### 1. Clone the Repository

First, clone this repository to your local machine.

```bash
git clone [Your GitHub Repository URL]
cd GeoNetRealtimeEarthquakeReporter
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

⚠️ Do not commit .env. Use .env.example to share safe templates.

An `.env.example` file is included to provide a safe template for environment variables.


### 5. Run the Application

The application consists of two parts:

#### a. Start the Notification Scheduler (Run in a separate terminal)

This monitors for major earthquakes in the background and generates notifications.

a. Start Notification Scheduler
```bash
python notification_scheduler.py
```

#### b. Start the Streamlit App (Run in another separate terminal)

This launches the main web application.

b. Start Streamlit App
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

## ✅ Implemented Improvements (Phase 1 Complete)

- **Notification Feature (Alert System)**:
  - Uses `apscheduler` to monitor the GeoNet API in the background
  - If an earthquake ≥ M4.0 is detected, a message is written to `notification_status.txt`
  - The Streamlit app reads this file and displays alerts in the UI

- **Urban Impact Map - Population Data Integration (Initial)**:
  - Integrated Stats NZ Spatial Query API to fetch population data near epicenters
  - Uses `STATS_NZ_API_KEY` from `.env`
  - Displays raw JSON output in the UI for transparency and debugging

## 🔭 Future Improvement Ideas (Phase 2 onwards)

1. **Enhanced Notification System**  
   Implement real-time alerts via email, SMS, or messaging platforms:
   - Use services like SendGrid, Twilio, or free alternatives such as Discord/Slack webhooks
   - Enable proactive communication for emergency response teams

2. **Historical Earthquake Data Acquisition**  
   Programmatically fetch and analyze historical data for ML training:
   - Use GeoNet’s `/quake?MMI=(int)` endpoint to retrieve events from the past 365 days
   - Build datasets for temporal and spatial modeling

3. **Urban Impact Map – Full ML/DL Integration**  
   Develop predictive models for earthquake vulnerability:
   - **GIS Layers Acquisition**: Building outlines (LINZ), geological maps/fault lines (GNS Science)
   - **Feature Engineering**: Combine seismic history with spatial layers
   - **Model Training**: Train ML/DL models for damage prediction
   - **GIS Visualization**: Display risk scores or heatmaps on the map

4. **Real-time LLM Enhancement**  
   Refine prompt logic to generate deeper insights:
   - Identify most affected cities
   - Recommend countermeasures or preparedness actions
   - Tailor messaging based on severity and population context

5. **User-Specific Reports (Prompt Tuning)**  
   Customize LLM output based on user roles:
   - Urban planners → infrastructure impact
   - Real estate agents → land use and valuation
   - Disaster management personnel → emergency response and public messaging

## 🛠️ DevOps & LLMOps Alignment

This project reflects key principles of DevOps and LLMOps:

- **Infrastructure as Code**: Environment setup is fully scripted via virtualenv, `.env.example`, and modular components.
- **CI/CD Readiness**: The architecture separates notification logic and UI, enabling scalable deployment and testing.
- **LLMOps Control**: Prompt logic is externalized in `.llm_prompt.txt`, allowing reproducible and auditable LLM behavior across environments.

---

## 🚀 Long-Term Vision (Phase 3 and Beyond)

This phase introduces a Model Context Protocol (MCP)-inspired architecture, designed to separate prompt logic, data access, and environment control—ensuring reproducibility, auditability, and safe deployment in public and educational settings.


6. **🧠 MCP-Enabled LLM Integration**  
   Enable Ollama or other LLMs to autonomously access real-time data via a structured MCP server:  
   - LLMs retrieve GeoNet and Stats NZ data through controlled interfaces  
   - Promotes secure, reproducible, and scalable AI reasoning workflows  
   - Ideal for public-sector deployments requiring transparency and data governance

7. **🧭 Dockerized MCP Server for Public Institutions**  
   Package the MCP server into a Docker container for easy deployment by LINZ, SCION, NIWA, and local councils:  
   - Ensures reproducibility and security in institutional environments  
   - Allows agencies to host their own GeoAI pipelines with minimal setup  
   - Supports integration with internal GIS layers and population datasets

8. **🧑‍🏫 Educational MCP Server for GeoAI Learning**  
   Provide a simplified MCP server for schools and universities:  
   - Students query real-time earthquake data and generate impact reports using LLMs  
   - Promotes hands-on learning in geospatial reasoning, disaster science, and AI ethics  
   - Enables reproducible classroom exercises with local data and controlled prompts

## 9. 🧩 Why This Architecture Matters

This project is more than a tool—it is a reproducible, auditable GeoAI pipeline designed for public institutions and classrooms.  
By separating prompt logic, environment variables, and data sources, it ensures trust, transparency, and adaptability across audiences.  
It reflects a Model Context Protocol (MCP)-like design philosophy, enabling safe deployment and educational clarity in geospatial reasoning.


