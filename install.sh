# Базовый образ
FROM python:3.9

# Устанавливаем нужные утилиты
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https

# Добавляем ключ и репозиторий Microsoft
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update

# Устанавливаем ODBC-драйвер и зависимости
RUN ACCEPT_EULA=Y apt-get install -y unixodbc-dev msodbcsql17

# Устанавливаем зависимости Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
