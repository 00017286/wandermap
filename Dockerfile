FROM python:3.9-slim-bullseye

USER root

# Устанавливаем переменную окружения для предотвращения ошибок с tzdata
ENV DEBIAN_FRONTEND=noninteractive

# Исправляем зеркала и HTTPS
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && apt-get update

# Устанавливаем утилиты
RUN apt-get update && apt-get install -y --fix-missing \
    curl gnupg2 apt-transport-https software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Добавляем Microsoft ODBC (если нужен SQL Server)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && apt-get install -y unixodbc unixodbc-dev odbcinst odbcinst1debian2 msodbcsql17

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app"]
