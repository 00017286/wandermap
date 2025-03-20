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

# Добавляем Microsoft ODBC (исправленный способ)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update 

RUN apt-get install -y unixodbc unixodbc-dev odbcinst odbcinst1debian2
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app"]
