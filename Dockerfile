FROM python:3.10.11-slim

WORKDIR /app

# Install system dependencies needed for compiling packages (like Rust extensions)
# This provides the 'cc' linker (gcc) that is missing.
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# 1. Copy requirements file
COPY requirements.txt .

# 2. Install dependencies (no cache to save space)
RUN pip install uv
RUN uv pip install --system --no-cache -r requirements.txt

# 3. Copy the rest of your application code
COPY . .

CMD ["python", "main.py"]