FROM python:3.9-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install pyodbc

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 10000

# CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]