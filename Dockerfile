# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app

# Install curl (needed for Docker healthcheck) + clean apt cache
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN pip install --no-cache-dir uv

# Copy dependency files first (better Docker layer caching)
COPY pyproject.toml uv.lock ./

# Install runtime dependencies (no dev deps)
RUN uv sync --frozen --no-dev

# Copy the rest of the project
COPY . .

EXPOSE 8000

# Run the API
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
