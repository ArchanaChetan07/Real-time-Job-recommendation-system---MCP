# Build from project root: docker build -t job-recommender .
FROM python:3.13-slim

WORKDIR /app

# Install deps from pyproject.toml
COPY pyproject.toml .
RUN pip install --no-cache-dir pip -q && pip install --no-cache-dir "streamlit>=1.45" "openai>=1.84" "pymupdf>=1.26" "python-dotenv>=1.1" "apify-client>=1.10"

COPY src/ src/
COPY app.py .

# Streamlit default port
EXPOSE 8501

# Health check: Streamlit serves on 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=2 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
