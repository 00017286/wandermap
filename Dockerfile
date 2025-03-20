# Используем buster вместо bullseye
FROM python:3.9-slim-buster

# Устанавливаем утилиты и зависимости
USER root
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https software-properties-common

# Исправляем URL на HTTPS
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list

# Добавляем репозиторий Microsoft ODBC
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update

# Проверяем доступные пакеты ODBC (для отладки)
RUN apt-cache search msodbcsql

# Удаляем кеш и устанавливаем пакеты
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --fix-missing unixodbc unixodbc-dev odbcinst odbcinst1debian2 msodbcsql17

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение
CMD ["gunicorn", "app:app"]
