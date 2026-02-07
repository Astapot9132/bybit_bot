FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "\
    echo 'Applying migrations...' && \
    python -m alembic upgrade heads && \
    echo 'Starting application...' && \
    python main.py\
"]