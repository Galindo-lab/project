#!/bin/bash
sudo docker compose -f docker-compose.yml exec -it web python3 manage.py makemigrations core
sudo docker compose -f docker-compose.yml exec -it web python3 manage.py migrate core