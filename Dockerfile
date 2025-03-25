FROM python:3.9-slim

# Установка зависимостей для ODBC драйвера и компилятора
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    msodbcsql17 \
    g++ \
    python3-dev \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Обновление pip
RUN pip install --upgrade pip

# Установка зависимостей из requirements.txt
COPY requirements.txt . 
RUN pip install -r requirements.txt

# Копирование всех файлов в контейнер
COPY . /app
WORKDIR /app

# Открытие порта
EXPOSE 10000

# Запуск приложения через Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
