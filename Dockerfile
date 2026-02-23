FROM python:3.12.6-slim-buster

WORKDIR /app

# System dependencies (recommended)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (cache optimization)
COPY requirements.txt .

# Upgrade pip + increase timeout
RUN pip install --upgrade pip \
    && pip install --default-timeout=300 -r requirements.txt

# Now copy rest of the app
COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
