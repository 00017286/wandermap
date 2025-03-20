# Базовый образ с поддержкой ODBC-драйвера
FROM python:3.9

# Устанавливаем зависимости
USER root
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y curl unixodbc-dev msodbcsql17

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение
CMD ["gunicorn", "app:app"]
