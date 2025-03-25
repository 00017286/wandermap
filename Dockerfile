# Используем официальный Python-образ
FROM python:3.9-slim

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    curl \
    gnupg2 \
    lsb-release \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости проекта
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копируем остальной код проекта
COPY . /app/

# Указываем команду запуска
CMD ["gunicorn", "-w", "3", "app:app"]
