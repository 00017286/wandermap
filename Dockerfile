FROM python:3.9-slim

# Устанавливаем необходимые пакеты с правами root
USER root

RUN apt-get update && \
    apt-get install -y unixodbc-dev msodbcsql17

# Устанавливаем зависимости Python
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем код приложения
COPY . /app

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "app.py"]
