# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install OS-level dependencies required for Chroma + DuckDB + PDF parsing
RUN apt-get update && apt-get install -y \
    gcc g++ build-essential \
    libglib2.0-0 libsm6 libxext6 libxrender1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
