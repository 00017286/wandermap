#!/bin/bash

# Останавливаем выполнение скрипта при ошибке
set -e

echo "Начало установки ODBC-драйверов..."

# Создаем директорию для конфигурации ODBC
mkdir -p ~/.odbcinst

# Добавляем драйвер в конфиг ODBC (обнови путь, если он отличается)
echo "[ODBC Driver 17 for SQL Server]" > ~/.odbcinst/odbcinst.ini
echo "Driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.1.1" >> ~/.odbcinst/odbcinst.ini

# Экспортируем переменные окружения для ODBC
export ODBCINI=~/.odbcinst/odbcinst.ini
export ODBCSYSINI=~/.odbcinst

echo "
