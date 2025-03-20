#!/bin/bash

# Установить ODBC-драйвер (если не установлен)
if ! command -v odbcinst &> /dev/null; then
    echo "Installing unixODBC and ODBC Driver 17..."
    sudo apt-get update && sudo apt-get install -y unixodbc unixodbc-dev odbcinst odbc-driver-mssql
fi

# Запустить приложение
exec gunicorn app:app
