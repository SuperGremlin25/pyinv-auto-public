# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for PyPDF2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY pyinv_auto.py .
COPY config.json .

# Create necessary directories
RUN mkdir -p /app/invoices /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Volume mounts for persistent data
VOLUME ["/app/invoices", "/app/logs", "/app/output"]

# Run the application in process-only mode by default
# Users can override with docker run command
CMD ["python", "pyinv_auto.py", "--process-only"]
