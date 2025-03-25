FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    msodbcsql17 \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Открытие порта
EXPOSE 10000

# Запуск приложения через Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]