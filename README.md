# NCR Property Intelligence 🏙️

The **NCR Property Intelligence** suite is an enterprise-grade investment discovery platform that leverages hyper-local spatial intelligence and machine learning to identify high-yield real estate opportunities across the National Capital Region (Gurgaon, Noida, Delhi, Greater Noida, Ghaziabad, and Faridabad).

## 🚀 Key Production Features

- **AI Investment Auditor**: Every listing is cross-referenced against a **Hyper-Local H3 Spatial Median** to assign visual value badges (🟢 Great Value, Good Deal, Premium).
- **"Best Deal" Discovery**: Aggressive deduplication filters out agent-listing noise, ensuring only the most competitive price variant for any given property is surfaced.
- **Market Analyzer Dashboard**: Dual-mode UI allows micro-market analysis, verified comparable generation, and 3D H3 hotspot visualizations.
- **Micro-Market Analysis**: Real-time rental yield and ROI calculations based on localized rental benchmark indices.

---

## 📐 System Architecture

The suite is architected as a fully decoupled, containerized micro-service environment designed for EC2 deployments:

1. **Intelligence Engine (FastAPI Backend)**
   - **H3 Auditor**: Uses Uber's H3 spatial indexing to cluster and benchmark property values.
   - **Inference Engine**: Handles ML-driven price predictions using pre-cached CatBoost models.
   - **Container**: Packaged via `Dockerfile` (optimized multi-stage build).

2. **Frontend Dashboard (Streamlit)**
   - Interactive, sleek UI rendering premium property cards and 3D PyDeck maps.
   - Mobile-responsive layout decoupled from massive ML backend libraries.
   - **Container**: Packaged via `Dockerfile.frontend` securely bridging internal API networks.

---

## 📦 Containerization & Deployment (Docker)

The repository is built for **GitHub Actions CI/CD** and automated deployment to AWS EC2. 
Both containers are strictly optimized utilizing **`python:3.11-slim`** base images and multi-stage builds to ensure incredibly small footprint deployment sizes (perfect for AWS Free Tier constraints).

### Quickstart (Local Docker-Compose)
To spin up the entire isolated network (UI + API) locally:
```bash
docker-compose up -d --build
```
- **UI Dashboard**: `http://localhost:8501`
- **Backend API Docs**: `http://localhost:8000/docs`

---

## 🗂️ Project Structure

```text
ncr_property_intelligence_system/
├── frontend/               # UI Dashboard (Streamlit)
│   ├── app.py              # Main frontend layout
│   └── style.css           # Custom sleek UI designs
├── ncr_property_price_estimation/
│   ├── intelligence/       # AI Auditor & Matching Engine
│   └── api.py              # FastAPI Service & Endpoints
├── data/                   # H3 Spatial indices & lookup tables
├── docker-compose.yml      # Local dev multi-container orchestrator
├── deploy_ec2.sh           # Remote server deployment script
├── Dockerfile              # Heavy Backend ML Image Build
├── Dockerfile.frontend     # Lightweight Streamlit Image Build
├── requirements_api.txt    # ML and FastApi Dependencies
└── requirements_frontend.txt # UI-only dependencies (Streamlit, PyDeck)
```

---

## 🛤️ MLOps & Data Versioning

This project uses a production-hardened data pipeline to ensure reproducibility and high-performance inference.

- **DVC (Data Version Control)**: Since property databases and serialized `.pkl`/`.cbm` ML artifacts are large, they are managed via **DVC**. Run `dvc pull` to synchronize the latest production models before local system builds.
- **MLflow**: Training experiments, including hyperparameters for the scoring engines are tracked via **MLflow**.

---

## 🚀 How to Run Locally (Without Docker)

### 1. Environment Setup
```bash
git clone https://github.com/anixes/ncr_property_intelligence_system.git
cd ncr_property_intelligence_system
python -m venv venv

# Windows
venv\Scripts\activate
# MacOS/Linux
source venv/bin/activate
```

### 2. Pull Production Assets
```bash
dvc pull
```

### 3. Start Services
Open two terminal windows:
```bash
# Terminal 1: Install & Start Backend
pip install -r requirements_api.txt
uvicorn ncr_property_price_estimation.api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Install & Start UI
pip install -r requirements_frontend.txt
streamlit run frontend/app.py
```
