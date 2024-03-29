#!/bin/sh
echo "Starting ..."

echo ">> Deleting old migrations"
find . -path "./apps/*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "./apps/*/migrations/*.pyc"  -delete


# Optional
echo ">> Deleting sqlite  (if exists) database"
find . -name "db.sqlite3" -delete

echo ">> Running manage.py makemigrations"
python manage.py makemigrations

echo ">> Running manage.py migrate"
python manage.py migrate

echo ">> Done"
