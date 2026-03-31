# ---------- 1. BUILDER STAGE ----------
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and enable buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /install

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install production dependencies to a prefix
COPY requirements_api.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements_api.txt

# OPTIONAL: Remove heavy NVIDIA/CUDA binaries if not using GPU
# This can save ~1GB if CatBoost pulls in GPU dependencies
RUN find /install -name "nvidia*" -type d -exec rm -rf {} + || true


# ---------- 2. RUNTIME STAGE ----------
FROM python:3.11-slim

LABEL maintainer="Anixes <anixes@dagshub.com>"
LABEL version="2.0.0"
LABEL description="NCR Property Intelligence - Production API"

# Runtime Environment
ENV TZ=UTC
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Create a non-root user for security (DevSecOps best practice)
RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin appuser

# Install runtime-only utilities (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the installed packages from builder
COPY --from=builder /install/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /install/bin /usr/local/bin

# Copy source code and artifacts with correct ownership
COPY --chown=appuser:appgroup ncr_property_price_estimation/ ncr_property_price_estimation/
COPY --chown=appuser:appgroup models/ models/
COPY --chown=appuser:appgroup data/ data/

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check (Standardized)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run API
CMD ["uvicorn", "ncr_property_price_estimation.api:app", "--host", "0.0.0.0", "--port", "8000"]
