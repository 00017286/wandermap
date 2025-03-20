FROM python:3.9-slim-bullseye

USER root
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https software-properties-common

# Исправляем HTTP → HTTPS
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list

# Добавляем репозиторий Microsoft ODBC
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update

# Очистка кеша перед установкой
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && apt-get update

# Устанавливаем ODBC-драйвер и зависимости
RUN ACCEPT_EULA=Y apt-get install -y --fix-missing unixodbc unixodbc-dev odbcinst odbcinst1debian2 msodbcsql17

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app"]
