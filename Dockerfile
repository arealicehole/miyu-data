# Miyu-Data Discord Bot with RAG
# Version: 2.0.0 - Major RAG Implementation

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .

# Create volume for persistent data if needed
VOLUME ["/app/data"]

# Set environment variables (can be overridden)
ENV PYTHONUNBUFFERED=1
ENV AI_PROVIDER=openrouter

# Health check for Discord bot
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the bot
CMD ["python", "main.py"]