# Используем официальный образ Debian 11 (Bullseye) с Python 3.9
FROM python:3.9

# Устанавливаем нужные утилиты
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https software-properties-common

# Добавляем репозиторий Microsoft (диагностика включена)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl -fsSL https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    apt-cache search msodbcsql || echo "ODBC-драйверы не найдены!"

# Устанавливаем ODBC-драйвер и зависимости (ставим msodbcsql18 вместо msodbcsql17)
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
