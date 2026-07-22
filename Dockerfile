# Beijing News Pipeline - Railway Dockerfile
# FastAPI serves both the API and frontend static files

FROM python:3.12-slim

WORKDIR /app

# Install API dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY api/ ./api/
COPY scrapers/ ./scrapers/
COPY scripts/ ./scripts/
COPY frontend/dist/ ./frontend/dist/
COPY sql/ ./sql/

# Install build-essential for scrapers (bs4 needs lxml which needs a C compiler)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install scraper dependencies
COPY scripts/requirements.txt ./scripts/
RUN pip install --no-cache-dir -r scripts/requirements.txt

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
