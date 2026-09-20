# 🌀 CycloneAI — Tropical Cyclone Identification, Classification & Prediction System

[![SIH Prototype](https://img.shields.io/badge/SIH-2026_Prototype-cyan.svg)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Vite](https://img.shields.io/badge/Frontend-React_18_%2B_Vite-61dafb.svg)](https://vitejs.dev/)
[![PyTorch](https://img.shields.io/badge/Deep%20Learning-PyTorch-ee4c2c.svg)](https://pytorch.org/)

> **Smart India Hackathon (SIH) Problem Statement:**  
> *"To develop an Artificial Intelligence (AI) / Machine Learning (ML) based system for identification, classification, and prediction of different tropical cyclone patterns using multi-source satellite data."*

---

## 🛰️ Project Overview

**CycloneAI** is an AI-powered command-center web application designed for meteorologists, disaster management authorities, and researchers. It integrates multi-spectral satellite imagery (INSAT-3D, GOES, Himawari, Sentinel) with deep convolutional neural networks and synoptic trajectory models to automate the cyclone monitoring lifecycle:

1. **Vortex & Eyewall Detection:** Identifies cyclonic spiral structure and estimates center-of-circulation coordinates.
2. **Intensity Classification:** Classifies storm intensity according to official **IMD / WMO** scales (Depression through Super Cyclone) with associated wind speed and central pressure estimates.
3. **Explainable AI (XAI):** Generates **Grad-CAM attention heatmaps** side-by-side with original satellite observations to visually explain neural network feature importance.
4. **48-Hour Forward Trajectory Prediction:** Predicts latitude, longitude, and intensity progression for **+6h, +12h, +24h, +36h, and +48h** forecast horizons using physical Coriolis recurvature dynamics.
5. **Interactive Geospatial Dashboard:** High-tech Leaflet map interface with historical track fixes, active eye position, predicted path lines, and coordinate/place search.
6. **Code-Free Dataset Manager:** Drag-and-drop ingestion of `.csv`, `.json`, `.nc` (NetCDF), and imagery files (`.png`, `.jpg`, `.tif`) without altering source code.
7. **Zero-Fake Model Analytics:** Authentic validation accuracy, precision, recall, F1, confusion matrix, and geodesic track error (km) calculated on real test partitions.

> [!IMPORTANT]
> **Research Prototype Disclaimer:**  
> *Research prototype for cyclone analysis. Forecast outputs must not replace official meteorological warnings from the India Meteorological Department (IMD) or national disaster management authorities.*

---

## 🏛️ System Architecture

```
Satellite Data Sources (INSAT-3D, GOES, NetCDF, GeoTIFF, CSV)
                         │
                         ▼
             Data Ingestion Layer (Dataset Manager)
                         │
                         ▼
        Preprocessing Pipeline (CLAHE, Normalization, Noise Reduction)
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
Cyclone Detection & Eye Centroid    Intensity Classification (IMD Scale)
         │                               │
         ▼                               ▼
Explainability Engine (Grad-CAM)    Track & Intensity Forecaster (+6h to +48h)
         │                               │
         └───────────────┬───────────────┘
                         ▼
                 FastAPI Backend API
                         │
                         ▼
              React Command Center Dashboard
    ┌────────────────────┴────────────────────┐
    ▼                                         ▼
Interactive Leaflet Map             Side-by-Side Saliency Viewer
(Forecast Track, Past Fixes)        (Original Satellite & Heatmap)
```

---

## ⚡ Technology Stack

### Frontend
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS (Dark navy command center palette with cyan/blue accents)
- **Maps:** Leaflet & React-Leaflet with custom SVG markers and tile selectors
- **Charts:** Recharts (Dual-axis wind speed & pressure curves, loss/acc epoch curves)
- **Icons:** Lucide React

### Backend & API
- **Language:** Python 3.12
- **Framework:** FastAPI with Uvicorn ASGI
- **Validation:** Pydantic v2
- **Database:** SQLite (modular design ready for PostgreSQL / PostGIS)

### AI / ML & Geospatial
- **Vision Models:** PyTorch & Torchvision (MobileNetV3 / ResNet18 backbone)
- **Trajectory Modeling:** Scikit-learn (Multi-Output Gradient Boosted Regressor)
- **Computer Vision:** OpenCV (`cv2`) & Pillow (`PIL`)
- **Geodesy:** Haversine formula, spherical bearing math & Geopy
- **NetCDF:** Adaptable NetCDF-4 / xarray reader

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.12)
- **Node.js 18+** & `npm`

---

### One-Click Launch (Recommended)

#### On Windows:
```powershell
.\run.ps1
```

#### On Linux / macOS:
```bash
chmod +x run.sh
./run.sh
```

---

### Manual Launch

#### Step 1: Backend Setup
```bash
# 1. Navigate to project root
cd cyclovision

# 2. (Optional) Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 4. Start FastAPI server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend runs on: [http://127.0.0.1:8000](http://127.0.0.1:8000)*  
*Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

#### Step 2: Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
*Frontend application launches at: [http://localhost:5173](http://localhost:5173)*

---

### Docker Compose (Optional)
```bash
docker-compose up --build
```

---

## 🎯 SIH Presentation Workflow (Step-by-Step Demo)

Judges and non-technical stakeholders can easily navigate the complete demonstration flow:

1. **Open Dashboard (`http://localhost:5173`)**:
   - Note the **"Demonstration Dataset"** badge and academic disclaimer.
   - Observe **Demo Cyclone 01** in the Bay of Bengal moving toward coastal India.
2. **Search Bar Demonstration**:
   - Type `"Odisha"`, `"Visakhapatnam"`, `"Bay of Bengal"`, or `"15.2, 84.7"`.
   - Show how the system calculates distance to the active storm and provides an estimated trajectory advisory.
3. **Interactive Cyclone Map**:
   - Inspect the **Blue Marker** (active storm eye with radar pulse).
   - Inspect the **Red Trajectory Line** and **Orange Forecast Fixes**.
   - Click markers to view popups with wind speed, pressure, and forecast hour.
4. **Side-by-Side Saliency Viewer**:
   - View the original infrared satellite observation alongside the **AI Attention Heatmap**.
   - Note the required explainability caption: *"AI Attention Region — areas highlighted by the model as important for cyclone identification."*
5. **Numerical Forecast Schedule & Charts**:
   - Review projected values for **+6h, +12h, +24h, +36h, +48h** with *"model estimate"* labels.
   - Inspect the dual-axis Recharts graph showing wind speed intensification and pressure drop.
6. **Live AI Detection Page**:
   - Switch to **Cyclone Detection** tab.
   - Click *"Load Calibrated Sample"* or upload an image to trigger the real-time neural pipeline with visible progress steps.
7. **Dataset Manager**:
   - Switch to **Datasets** tab.
   - Drag-and-drop a new `.csv` or satellite image.
   - View automatic format detection, metadata inspection, and click *"Run Analysis"* without touching source code.
8. **Model Analytics**:
   - Switch to **Model Analytics** tab.
   - Demonstrate genuine validation metrics, the intensity confusion matrix, and track geodesic error breakdown in km.

---

## 📊 Evaluation & Model Training

To train or evaluate models directly via CLI:

```bash
# 1. Train Satellite Vision Classifier
python scripts/train_classifier.py

# 2. Train Trajectory Forecaster
python scripts/train_track_model.py

# 3. Evaluate Classifier (Accuracy, Precision, Recall, Confusion Matrix)
python scripts/evaluate_classifier.py

# 4. Evaluate Track Forecaster (MAE, RMSE, km geodesic distance error)
python scripts/evaluate_track_model.py

# 5. Generate Grad-CAM Heatmap from CLI
python scripts/generate_heatmap.py --image data/demo/demo_satellite_ir.png
```

---

## 📁 Repository Structure

```
cyclovision/
├── backend/
│   ├── api/
│   │   ├── routes_health.py         # /api/health
│   │   ├── routes_cyclones.py       # /api/cyclones, /api/search
│   │   ├── routes_analysis.py       # /api/analyze, /api/detect, /api/classify, /api/predict-track
│   │   ├── routes_datasets.py       # /api/datasets, /api/datasets/upload
│   │   └── routes_models.py         # /api/model/metrics, /api/model/train
│   ├── database/
│   │   ├── db.py                    # SQLite connection & table schemas
│   │   └── models.py                # Database entity mappings
│   ├── schemas/
│   │   └── schemas.py               # Pydantic schemas for all payloads
│   ├── services/
│   │   ├── demo_service.py          # Demo dataset generator & seeder
│   │   └── dataset_service.py       # Multi-format dataset ingestion & validation
│   ├── config.py                    # App configuration, IMD scales & disclaimers
│   └── main.py                      # FastAPI application entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx           # Command center navigation bar
│   │   │   ├── SearchBar.jsx        # Geocoding & coordinate search
│   │   │   ├── StatusCard.jsx       # Top 4 KPI status cards
│   │   │   ├── CycloneMap.jsx       # Leaflet interactive map with custom SVG markers
│   │   │   ├── CycloneInfoPanel.jsx # Meteorological stats & landfall advisories
│   │   │   ├── SatelliteViewer.jsx  # Original satellite imagery viewer
│   │   │   ├── HeatmapViewer.jsx    # Grad-CAM explainability heatmap viewer
│   │   │   ├── ForecastTable.jsx    # +6h to +48h numerical schedule
│   │   │   ├── ForecastChart.jsx    # Recharts wind speed & pressure curves
│   │   │   ├── DatasetUploader.jsx  # Drag-and-drop dataset manager
│   │   │   └── ModelMetrics.jsx     # Confusion matrix & performance metrics
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx        # Main command center dashboard
│   │   │   ├── Detection.jsx        # Live satellite detection & Grad-CAM
│   │   │   ├── Prediction.jsx       # Interactive trajectory simulator
│   │   │   ├── Datasets.jsx         # Dataset management center
│   │   │   ├── Analytics.jsx        # Model performance analytics
│   │   │   └── About.jsx            # SIH project documentation & disclaimers
│   │   ├── services/
│   │   │   └── api.js               # Centralized Axios API client
│   │   ├── App.jsx                  # Main application wrapper
│   │   └── index.css                # Tailwind & custom radar styles
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── ml/
│   ├── detection/detector.py        # Cyclone pattern detection & vortex center estimation
│   ├── classification/classifier.py # IMD intensity classifier (Depression to Super Cyclone)
│   ├── prediction/track_predictor.py# +6h to +48h trajectory forecaster
│   ├── explainability/gradcam.py    # Grad-CAM deep attention heatmap generator
│   └── evaluation/evaluator.py      # Real scikit-learn metrics & geodesic km error calculator
│
├── preprocessing/
│   ├── image_preprocessing.py       # CLAHE contrast, bilateral noise reduction, normalization
│   ├── track_preprocessing.py       # Spherical bearing, Haversine distance, time-series features
│   ├── netcdf_preprocessing.py      # NetCDF-4 adapter for satellite brightness temperatures
│   └── augmentation.py              # Meteorological-safe image rotations and transformations
│
├── data/
│   ├── raw/                         # Raw incoming observation files
│   ├── processed/                   # Preprocessed tensor matrices
│   ├── satellite/                   # Folder for real INSAT/GOES satellite imagery
│   ├── tracks/                      # Folder for real IBTrACS track CSVs
│   └── demo/                        # Pre-generated Demo Cyclone 01 assets & metrics
│
├── models/
│   ├── classification/              # Saved PyTorch classifier weights (.pt)
│   └── prediction/                  # Saved scikit-learn track predictor weights (.joblib)
│
├── scripts/
│   ├── train_classifier.py          # Vision classifier training script
│   ├── train_track_model.py         # Track regressor training script
│   ├── evaluate_classifier.py       # Classification metrics & confusion matrix CLI
│   ├── evaluate_track_model.py      # Track prediction geodesic error CLI
│   └── generate_heatmap.py          # Standalone Grad-CAM heatmap CLI
│
├── tests/
│   ├── test_preprocessing.py        # Geospatial & image preprocessing unit tests
│   └── test_api.py                  # FastAPI endpoint integration tests
│
├── requirements.txt
├── docker-compose.yml
├── Dockerfile.backend
├── run.ps1                          # Windows PowerShell launcher
├── run.sh                           # Linux/macOS launcher
└── README.md
```

---

## 🔮 Future Roadmap

- [ ] **Live MOSDAC / ISRO Integration:** Automated periodic fetching of INSAT-3D/3DR TIR-1 and VIS frames.
- [ ] **NOAA / IBTrACS Live Sync:** Continuous ingestion of global tropical storm advisory bulletins.
- [ ] **YOLOv11-OBB Object Detection:** Oriented bounding boxes for asymmetric multi-cyclone systems.
- [ ] **Transformer-Based Spatiotemporal Forecaster:** Swin-LSTM or Trajectory Transformer for 72-hour forecasting.
- [ ] **Coastal Storm Surge & Rainfall Modeling:** Coupling hydrodynamic inundation models with predicted storm landfall coordinates.

---

## 👥 Contributors

Built for the **Smart India Hackathon (SIH)**.
Licensed under the [MIT License](LICENSE).
