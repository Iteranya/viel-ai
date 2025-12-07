# Use a lightweight Python Linux image
FROM python:3.10.11-slim

# Set the working directory inside the container
WORKDIR /app

# 1. Copy requirements first (for Docker caching speed)
COPY requirements.txt .

# 2. Install dependencies (no cache to save space)
RUN pip install uv
RUN uv pip install --system --no-cache -r requirements.txt

# 3. Copy the rest of your application code
COPY . .

# Tell Docker we use port 5666
EXPOSE 5666

# Start the application
CMD ["python", "main.py"]