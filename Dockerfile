FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2, etc.
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy only lockfiles & install deps
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# Copy source
COPY . .

EXPOSE 8501

CMD ["poetry", "run", "streamlit", "run", "app/ui/app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
