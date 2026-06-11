# Crop Profit Forecasting System

A machine learning application that combines USDA crop yield data and historical weather data to predict crop yields and support future crop profitability analysis.

---

## Data

USDA Crop Data:
https://quickstats.nass.usda.gov/

Weather Data:
https://open-meteo.com/

---

## Setup

### 1. Create a Virtual Environment

Linux / macOS / WSL:

```bash
python3 -m venv venv
```

Windows:

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

Linux / macOS / WSL:

```bash
source venv/bin/activate
```

Windows Command Prompt:

```cmd
venv\Scripts\activate
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Building the Dataset


#### 1. Build Weather Dataset

```bash
python -m ml.data.build_weather_data
```

Creates:

```text
ml/data/weather_data.csv
```

#### 2. Build Crop Yield Dataset

```bash
python -m ml.data.build_yield_data
```

Creates:

```text
ml/data/yield_data.csv
```
---

## Training the Model

Train the Random Forest yield prediction model:

```bash
python ml/train.py
```

Creates:

```text
ml/crop_model.pkl
```

---

## Running the Backend

Start the FastAPI server:

```bash
uvicorn backend.app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

### Install Frontend Dependencies

```bash
cd frontend
npm install
npm install recharts
```

### Run Frontend

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---