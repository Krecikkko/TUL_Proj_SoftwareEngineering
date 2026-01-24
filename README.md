# Energy Management System in Intelligent Buildings (EMSIB)

## Project Overview
The **EMSIB** platform is an intelligent IT system designed for energy management in commercial and public buildings. Its primary goal is to optimize energy consumption, minimize operating costs, improve user comfort, and support sustainable development by reducing the carbon footprint.

The system enables real-time monitoring, analysis, forecasting, and automatic control of energy-consuming devices, ensuring flexibility and adaptation to changing conditions.

### Key Benefits
* **Cost Reduction**: optimizing energy consumption to achieve significant savings.
* **User Comfort**: intelligent control of climate and lighting conditions.
* **Operational Efficiency**: automating management processes for maintenance engineers.
* **Sustainability**: supporting the reduction of CO2 emissions.

## System Architecture

The system follows a three-tier architecture:

### 1. Presentation Layer (Frontend)
* **Technologies**: React (Vite)
* **Modules**:
    * **UI/UX**: Dashboard for building administrators and maintenance engineers.
    * **Data Visualization**: specialized views for analyzing energy consumption charts and reports.

### 2. Business Logic Layer (Backend)
* **Technologies**: Python (FastAPI)
* **Microservices**:
    * **Alerts, Authentication, and Communication (AAC)**: Handles user authentication, alert generation, and notifications.
    * **Data Access and Control (DAC)**: Manages core data, measurements, and device control logic.
    * **Forecast and Optimization**: Uses Machine Learning to predict energy demand and optimize costs.

### 3. Data Layer
* **Relational Database**: Stores core entities (Buildings, Devices, Users, Alerts) as defined in the core schema.
* **Time-Series/NoSQL**: Used for high-volume sensor data and measurements.

---

## Getting Started

### Prerequisites
* **Python 3.8+** (with `venv` support)
* **Node.js** (LTS version) & **npm**
* **Git**

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd emsib-platform
    ```

2.  **Backend Setup**:
    Navigate to each backend module (`backend/alerts...`, `backend/data...`, `backend/forecast...`) and create a virtual environment:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
    ```bash
    # Linux
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**:
    Navigate to `frontend/ui-ux` and `frontend/data-visualization` and install dependencies:
    ```bash
    npm install
    ```

### Running the System

You can run the system components manually or using the provided automation script.

#### Option A: Automated Script (Windows)
A PowerShell script is available to launch all services in separate tabs (requires Windows Terminal).
```powershell
./run.ps1
