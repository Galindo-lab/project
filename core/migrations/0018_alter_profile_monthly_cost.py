# Generated by Django 5.1.6 on 2025-05-18 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='monthly_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
