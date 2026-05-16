FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy training data and script
COPY data/ ./data/
COPY train.py .

# Default command: run training
CMD ["python", "train.py"]
