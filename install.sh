# Базовый образ
FROM python:3.9

# Устанавливаем нужные утилиты
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https software-properties-common

# Добавляем ключ Microsoft и репозиторий для Debian 11 (bullseye)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    add-apt-repository "$(curl -fsSL https://packages.microsoft.com/config/debian/11/prod.list)" && \
    apt-get update

# Устанавливаем ODBC-драйвер и зависимости
RUN ACCEPT_EULA=Y apt-get install -y unixodbc unixodbc-dev msodbcsql18

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
