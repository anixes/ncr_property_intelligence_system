# ---------- 1. BUILDER STAGE ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /install

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install frontend dependencies (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- 2. RUNTIME STAGE ----------
FROM python:3.11-slim

LABEL maintainer="Anixes <anixes@dagshub.com>"
LABEL version="2.0.0"
LABEL description="NCR Property Intelligence - Production Frontend"

ENV TZ=UTC
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Create a non-root user for security (Streamlit best practice)
RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin appuser

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /install/bin /usr/local/bin

# Copy frontend source code with correct ownership
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

EXPOSE 8501

# Health check (Streamlit standard)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run frontend using streamlit
# Added flags for production security
CMD ["streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--browser.gatherUsageStats", "false", \
     "--server.enableXsrfProtection", "true"]
