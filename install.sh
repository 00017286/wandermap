#!/bin/bash

# Останавливаем выполнение скрипта при ошибке
set -e

echo "Начало установки ODBC-драйверов..."

# Устанавливаем зависимости (без sudo)
apt-get update --allow-releaseinfo-change && apt-get install -y curl unixodbc-dev

# Скачиваем и устанавливаем Microsoft ODBC Driver 17 для SQL Server (без sudo)
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Создаем директорию для конфигурации ODBC
mkdir -p ~/.odbcinst

# Добавляем драйвер в конфиг ODBC
echo "[ODBC Driver 17 for SQL Server]" > ~/.odbcinst/odbcinst.ini
echo "Driver=$(find /opt/microsoft/msodbcsql17/lib64 -name 'libmsodbcsql-*.so.*' | head -n 1)" >> ~/.odbcinst/odbcinst.ini

# Экспортируем переменные окружения для ODBC
export ODBCINI=~/.odbcinst/odbcinst.ini
export ODBCSYSINI=~/.odbcinst

echo "Установка завершена!"
