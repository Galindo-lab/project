#!/bin/bash
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.create_superuser(username='test', email='test@example.com', password='123');
for i in range(1, 20):
    User.objects.create_user(username=f'user{i}', email=f'user{i}@example.com', password='123');
    "