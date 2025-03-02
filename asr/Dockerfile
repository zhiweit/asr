FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt ./requirements.txt

# Create virtual environment and install dependencies
RUN uv venv && . .venv/bin/activate && uv pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose port
EXPOSE 8001

# Use the Python executable from the virtual environment explicitly
CMD ["/app/.venv/bin/python", "asr_api.py"]
