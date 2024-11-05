FROM python:3.9-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


RUN mkdir -p /app/app/api /app/app/services /app/app/db /app/tests


COPY . .


RUN touch /app/app/__init__.py \
    && touch /app/app/api/__init__.py \
    && touch /app/app/services/__init__.py \
    && touch /app/app/db/__init__.py \
    && touch /app/tests/__init__.py


ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 