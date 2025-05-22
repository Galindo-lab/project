#!/bin/bash
sudo docker compose exec -it web python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.exclude(is_superuser=True).delete();
print('Usuarios eliminados');
"