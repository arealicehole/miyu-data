# Miyu-Data Discord Bot with RAG
# Version: MDB2A (v2.0.0) - Optimized build

FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AI_PROVIDER=openrouter

# Run the bot
CMD ["python", "main.py"]