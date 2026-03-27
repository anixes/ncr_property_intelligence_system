FROM python:3.11-slim

# Set timezone explicitly and disable Python buffering/pyc
ENV TZ=UTC
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Install curl for healthcheck + clean up apt cache
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Install dependencies first (layer caching)
COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt

# 3. Copy source code package
COPY ncr_property_price_estimation/ ncr_property_price_estimation/

# 4. Copy consolidated data registry (H3 indices, locality maps)
COPY data/ data/

# 5. Copy model artifact (joblib fallback)
COPY models/pipeline_v1.joblib models/pipeline_v1.joblib

# 5. Expose the port
EXPOSE 8000

# 6. Health check so orchestrators can detect unhealthy containers
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 7. Run API using the module path
CMD ["uvicorn", "ncr_property_price_estimation.api:app", "--host", "0.0.0.0", "--port", "8000"]
