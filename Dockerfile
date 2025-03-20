# Базовый образ
FROM python:3.9-slim-bullseye

# Устанавливаем утилиты и зависимости
USER root
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https software-properties-common

# Добавляем репозиторий Microsoft ODBC (используем buster, если bullseye не работает)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update

# Проверяем доступные пакеты ODBC (для отладки)
RUN apt-cache search msodbcsql

# Устанавливаем ODBC-драйвер и зависимости
RUN ACCEPT_EULA=Y apt-get install -y unixodbc unixodbc-dev odbcinst odbcinst1debian2 msodbcsql17

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение
CMD ["gunicorn", "app:app"]
