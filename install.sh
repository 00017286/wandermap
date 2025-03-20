#!/bin/bash

set -e

echo "Начало установки ODBC-драйверов..."

apt-get update && apt-get install -y curl unixodbc-dev

curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" | tee /etc/apt/sources.list.d/mssql-release.list
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

mkdir -p ~/.odbcinst

echo "[ODBC Driver 17 for SQL Server]" > ~/.odbcinst/odbcinst.ini
echo "Driver=$(find /opt/microsoft/msodbcsql17/lib64 -name 'libmsodbcsql-*.so.*' | head -n 1)" >> ~/.odbcinst/odbcinst.ini

export ODBCINI=~/.odbcinst/odbcinst.ini
export ODBCSYSINI=~/.odbcinst

echo "Установка завершена!"