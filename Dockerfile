# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

# Install uv binary directly
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# (Optional) Install build-essential ONLY in the builder stage
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy only dependency files first (for better layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment (.venv)
# --frozen: ensures uv.lock is not modified
# --no-install-project: avoids installing the app itself in this step
RUN uv sync --frozen --no-cache --no-install-project


# --- Stage 2: Runtime ---
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy your application code
COPY . .

# IMPORTANT: Place the virtual environment's bin folder at the front of the PATH.
# This makes 'python' refer to the one in the venv automatically.
ENV PATH="/app/.venv/bin:$PATH"

# No need to use 'uv run' here because the PATH is set
CMD ["python", "main.py"]