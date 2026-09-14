FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required by OpenCV and PaddlePaddle
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libegl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Cloud Run uses the $PORT environment variable (defaults to 8080)
EXPOSE 8080

# Start the FastAPI application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
