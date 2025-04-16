#!/bin/bash

# Load variables from the .env file
set -o allexport
source .env
set -o allexport

# Wait for the database to be ready
echo -e "\e[34mWaiting for the database to become available...\e[0m"  # Blue message

# Try to connect to the host 'db' on port 3306 until successful
until nc -z -v -w30 db 3306
do
  echo -e "\e[34mWaiting for the database to become available...\e[0m"  # Blue message
  sleep 5
done

# Success message in green when the database is ready
echo -e "\e[32mThe database is ready. Running migrations and collecting static files.\e[0m"  # Green message

# Run migrations and collect static files
python manage.py collectstatic --noinput
python manage.py migrate

# Success message in green after successful migrations
echo -e "\e[32mMigrations and static files collected successfully.\e[0m"  # Green message

# Change permissions for the media directory
chmod -R 777 /code/media





# Convert the value of DEBUG to lowercase to avoid case issues
debug=$(echo "$DEBUG" | tr '[:upper:]' '[:lower:]')
if [ "$debug" = "true" ]; then
  echo -e "\e[31mDEBUG MODE ACTIVATED\e[0m"  # Red message for debug mode
fi




# Convert the value of DEBUG to lowercase to avoid case issues
mode=$(echo "$MODE" | tr '[:upper:]' '[:lower:]')
if [ "$mode" = "dev" ]; then
  # Iniciar mkdocs en segundo plano
  echo "\e[34mStarting MkDOcs in the port 8001...\e[0m"
  mkdocs serve -a 0.0.0.0:8001 &  

  # Iniciar runserver en modo desarrollo
  echo -e "\e[31mStarting Django runserver in development mode...\e[0m"
  exec python3 manage.py runserver 0.0.0.0:80 
else
  # Iniciar Apache en primer plano
  echo -e "\e[34mStarting Apache in production mode...\e[0m"
  echo -e "\e[34mStarting Apache in the foreground...\e[0m"
  exec apachectl -D FOREGROUND
fi
