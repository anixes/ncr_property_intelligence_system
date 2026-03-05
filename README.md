# NCR Property Price Estimator 🏠

A complete end-to-end Machine Learning web application for predicting real estate prices in the National Capital Region (Delhi-NCR) of India. 

The project includes an entire ML pipeline: data processing, model training, an exposed **FastAPI** backend for predictions, and a polished **Streamlit** frontend interface. All components are containerized and orchestrated using **Docker Compose** for seamless CI/CD and deployment.

---

## 🏗️ System Architecture & Design

The application consists of three main logical components decoupled for scalability:

1. **Machine Learning Pipeline (`ncr_property_price_estimation/modeling`)**
   - Built with `scikit-learn` pipelines.
   - Includes custom transformers (Log/Winsorizer/Geo-Median Encoders) for robust data preprocessing.
   - The final artifact (`pipeline_v1.joblib`) is version-controlled separately using **DVC** and synced remotely.

2. **Backend API (`FastAPI`)**
   - Serves the serialized ML model via a high-performance REST API.
   - Implements robust Pydantic data validation for all incoming property configurations.
   - Accessible internally by the frontend or externally by 3rd-party services.

3. **Frontend Application (`Streamlit`)**
   - A modern, responsive Python-based UI styled with custom CSS for an enterprise look.
   - Interacts seamlessly with the FastAPI backend over HTTP to fetch and display predictions.

## 💻 Tech Stack

- **Machine Learning**: `scikit-learn`, `pandas`, `numpy`, `xgboost/lightgbm (optional)`
- **Experiment Tracking / MLOps**: `MLflow`, `DVC`
- **Backend**: `FastAPI`, `Uvicorn`, `Pydantic`
- **Frontend**: `Streamlit`, `Requests`
- **Containerization**: `Docker`, `Docker Compose`
- **CI/CD**: `GitHub Actions` (Linting, Test Suite, Docker Image Builds)
- **Formatting / Linting**: `Ruff`
- **Testing**: `Pytest`

---

## 🚀 How to Run Locally

### Approach 1: The Easy Way (Docker Compose)
*Best for running the entire stack (API + Frontend) at once without installing Python dependencies.*

Pre-requisites: Docker & Docker Compose installed.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anixes/ncr_property_price_estimation.git
   cd ncr_property_price_estimation
   ```

2. **Pull the ML Model (Optional if already checked in to LFS, but required for DVC):**
   ```bash
   dvc pull
   ```

3. **Build and start the services:**
   ```bash
   docker-compose up --build -d
   ```

4. **Access the application:**
   - 🏠 **Streamlit Frontend:** `http://localhost:8501`
   - ⚙️ **FastAPI Swagger Docs:** `http://localhost:8000/docs`

---

### Approach 2: Manual Development Mode
*Best if you want to actively modify code, train models, or run tests.*

1. **Clone and setup a virtual environment:**
   ```bash
   git clone https://github.com/anixes/ncr_property_price_estimation.git
   cd ncr_property_price_estimation
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements_production.txt
   pip install -r requirements_dev.txt
   ```

3. **Start the API:**
   ```bash
   uvicorn ncr_property_price_estimation.api:app --reload
   ```

4. **Start the Frontend (in a new terminal):**
   ```bash
   cd frontend
   python -m streamlit run app.py
   ```

---

## 🧪 Testing and CI/CD

The repository includes a comprehensive `pytest` suite for the ML features, pipelines, and FastAPI endpoints.
Continuous Integration (CI) is configured via **GitHub Actions** (`.github/workflows/ci.yml`) which automatically runs:
1. `ruff` checks and code formatting verification.
2. `pytest` for all unit and integration tests.
3. Tests checking that Docker images (API and Frontend) build successfully.

To run the test suite locally:
```bash
pytest -v
```

To run lint checks:
```bash
ruff check .
ruff format --check .
```
