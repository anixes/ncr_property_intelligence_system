# ---------- Builder stage ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/api.txt .

RUN pip install --no-cache-dir --prefix=/install -r api.txt


# ---------- Runtime stage ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy only installed packages from builder
COPY --from=builder /install /usr/local

# Copy code package and model artifact
# Note: models/pipeline_v1.joblib is pulled via DVC in CI before build
COPY ncr_property_price_estimation/ ncr_property_price_estimation/
COPY models/ models/

EXPOSE 8000

# Run API as a module
CMD ["uvicorn", "ncr_property_price_estimation.api:app", "--host", "0.0.0.0", "--port", "8000"]
