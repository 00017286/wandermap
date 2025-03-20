# Базовый образ с более новой версией Debian
FROM python:3.9-slim-bullseye

# Устанавливаем утилиты и зависимости
USER root
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https software-properties-common

# Добавляем ключи Microsoft и обновленный репозиторий для Bullseye
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update

# Устанавливаем ODBC-драйвер и зависимости
RUN ACCEPT_EULA=Y apt-get install -y unixodbc unixodbc-dev msodbcsql18

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение
CMD ["gunicorn", "app:app"]
