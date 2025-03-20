# Базовый образ
FROM python:3.9

# Устанавливаем утилиты и зависимости
USER root
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https software-properties-common

# Добавляем ключи и репозиторий Microsoft ODBC
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    add-apt-repository "$(curl -fsSL https://packages.microsoft.com/config/debian/10/prod.list)" && \
    apt-get update

# Устанавливаем ODBC-драйвер и зависимости
RUN ACCEPT_EULA=Y apt-get install -y unixodbc unixodbc-dev msodbcsql17

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение
CMD ["gunicorn", "app:app"]
