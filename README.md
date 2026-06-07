# Crop Profit Forecasting System

A machine learning application that combines USDA crop yield data and historical weather data to predict crop yields and support future crop profitability analysis.

---

## Project Overview

This project:

* Retrieves crop yield data from the USDA API
* Retrieves historical weather data from Open-Meteo
* Combines crop and weather data into a training dataset
* Trains a machine learning model to predict crop yield
* Serves predictions through a FastAPI backend
* Displays results through a React frontend

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

### Step 1: Fetch USDA Crop Yield Data

```bash
python -m ml.data.fetch_usda
```

Creates:

```text
ml/data/usda_yield.csv
```

---

### Step 2: Build the Training Dataset

```bash
python -m ml.data.build_training_data
```

This step:

* Loads USDA crop data
* Retrieves historical weather data
* Combines weather and crop information
* Creates the final ML dataset

Creates:

```text
ml/data/training_data.csv
```

---

## Training the Model

Train the Random Forest yield prediction model:

```bash
python ml/train_yield.py
```

Creates:

```text
ml/yield_model.pkl
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