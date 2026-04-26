# Use a multi-stage build to keep the final image clean
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

# Set environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Copy lock files and pyproject.toml first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# Install dependencies (excluding dev dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy the application code
COPY . .

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Final Stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy the virtual environment and application code from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Set environment variables to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
