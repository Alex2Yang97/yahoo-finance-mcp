# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS uv

# Install the project into /app
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy project files
COPY pyproject.toml .

# Install the project's dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e .

# Copy the rest of the application code
COPY . .

# Second stage: runtime image
FROM python:3.14-slim

WORKDIR /app

# Copy the virtual environment from the uv stage
COPY --from=uv /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=uv /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Command to run the MCP server
CMD ["uv", "run", "server.py"]
