#!/bin/sh

echo 'Esperando o PostgreSQL iniciar...'

while ! nc -z $DB_HOSTNAME $DB_PORT; do
    sleep 0.1
done

echo 'PostgreSQL iniciado'

echo 'Migrando banco de dados...'
python3 manage.py migrate

exec "$@"