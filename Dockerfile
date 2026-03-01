FROM python:3.11-slim

# Set timezone explicitly and disable Python buffering/pyc
ENV TZ=UTC
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Install dependencies first (layer caching)
COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt

# 2. Copy source code package
COPY ncr_property_price_estimation/ ncr_property_price_estimation/

# 3. Copy model artifact (joblib fallback)
# We bake the joblib inside the image for simplicity.
# At scale, this would be downloaded at runtime from MLflow/S3.
COPY models/pipeline_v1.joblib models/pipeline_v1.joblib

# 4. Expose the port
EXPOSE 8000

# 5. Run API using the module path
CMD ["uvicorn", "ncr_property_price_estimation.api:app", "--host", "0.0.0.0", "--port", "8000"]
