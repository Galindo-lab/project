# Generated by Django 5.1.6 on 2025-02-19 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_ubicacion_latitud_alter_ubicacion_longitud'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ubicacion',
            name='latitud',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='ubicacion',
            name='longitud',
            field=models.CharField(max_length=50),
        ),
    ]
