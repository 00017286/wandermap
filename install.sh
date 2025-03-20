#!/bin/bash
set -e

# Обновляем пакеты
apt-get update

# Устанавливаем unixODBC и зависимости
apt-get install -y curl gnupg apt-transport-https ca-certificates unixodbc unixodbc-dev odbcinst

# Добавляем ключи и репозиторий Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/$(lsb_release -rs)/prod $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/mssql-release.list

# Обновляем пакеты снова и устанавливаем ODBC Driver 17
apt-get update
apt-get install -y msodbcsql17

# Проверяем, что драйвер установлен
odbcinst -q -d
